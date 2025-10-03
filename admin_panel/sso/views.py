# admin_panel/sso/views.py
import json
import logging
from datetime import datetime, timezone

import httpx
from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.core.cache import cache
from django.http import (HttpRequest,
                         HttpResponse,
                         HttpResponseRedirect,
                         JsonResponse)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from jose import jwk, jwt
from jose.utils import base64url_decode

logger = logging.getLogger(__name__)

JWKS_CACHE_KEY = "sso:jwks"
JWKS_TTL = 600
CLOCK_SKEW = 30  # секунд допуска по часам


def _get_bearer_token(request: HttpRequest) -> str | None:
    # 1) Authorization header
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    # 2) ?token=...
    token = request.GET.get("token")
    if token:
        return token.strip()
    return None


def _get_jwks(force: bool = False) -> dict:
    if not force:
        jwks = cache.get(JWKS_CACHE_KEY)
        if jwks:
            return jwks
    resp = httpx.get(settings.AUTH_JWKS_URL, timeout=3.0)
    resp.raise_for_status()
    jwks = resp.json()
    cache.set(JWKS_CACHE_KEY, jwks, JWKS_TTL)
    kids = [k.get("kid") for k in jwks.get("keys", [])]
    logger.info("✅ JWKS fetched, kids=%s", kids)
    return jwks


def _pick_key(jwks: dict, kid: str) -> dict | None:
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            return k
    return None


def _verify_rs256(token: str, jwks: dict) -> dict:
    hdr = jwt.get_unverified_header(token)
    kid = hdr.get("kid")
    if not kid:
        raise ValueError("JWT header has no kid")

    # Разрешаем только RS256 (жёстче и безопаснее)
    alg = (hdr.get("alg") or "RS256").upper()
    if alg != "RS256":
        raise ValueError(f"Unexpected alg: {alg}")

    # подбираем ключ по kid
    key_dict = next((
        k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if not key_dict:
        # один раз обновляем JWKS и пробуем снова (ротация ключей)
        jwks = _get_jwks(force=True)
        key_dict = next((
            k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key_dict:
            raise ValueError(f"kid {kid} not found in JWKS")

    # 🔧 ВАЖНО: указываем алгоритм
    rsa_key = jwk.construct(key_dict, algorithm="RS256")

    try:
        h_b64, p_b64, s_b64 = token.split(".")
    except ValueError:
        raise ValueError("Malformed JWT")

    signing_input = f"{h_b64}.{p_b64}".encode("utf-8")
    signature = base64url_decode(s_b64.encode("utf-8"))

    if not rsa_key.verify(signing_input, signature):
        raise ValueError("Invalid JWT signature")

    claims = json.loads(
        base64url_decode(p_b64.encode("utf-8")).decode("utf-8")
    )

    # базовая валидация exp (можешь добавить nbf/iss при желании)
    now = datetime.now(timezone.utc).timestamp()
    exp = float(claims.get("exp", 0))
    if now >= exp:
        raise ValueError("JWT expired")

    return claims


def _is_allowed_admin(email: str | None) -> bool:
    if not email:
        return False
    return email.lower() in settings.ALLOWED_ADMIN_EMAILS


@csrf_exempt
def jwt_login(request: HttpRequest) -> HttpResponse:
    token = _get_bearer_token(request)
    if not token:
        return JsonResponse({"detail": "Missing Bearer token"}, status=401)

    try:
        jwks = _get_jwks()
    except Exception as e:
        logger.exception("JWKS fetch error: %s", e)
        return JsonResponse({"detail": "Auth service unavailable"}, status=503)

    try:
        claims = _verify_rs256(token, jwks)
    except Exception as e:
        logger.warning("JWT verify failed: %s", e)
        return JsonResponse({"detail": "Invalid token"}, status=401)

    sub = claims.get("sub")
    email = claims.get("email") or ""
    if not _is_allowed_admin(email):
        return JsonResponse(
            {"detail": "Forbidden (email not allowed)"},
            status=403
        )

    User = get_user_model()
    # username берём из email, fallback — sub
    username = email or sub
    if not username:
        return JsonResponse(
            {"detail": "Token missing subject/email"},
            status=400
        )

    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email, "is_staff": True, "is_active": True},
    )
    # Поддержим обновление email если изменился
    if email and user.email != email:
        user.email = email
        user.save(update_fields=["email"])

    # Можно маппить клеймы → флаги
    # user.is_superuser = True/False по какому-то признаку;
    # сейчас — только whitelist
    if not user.is_staff:
        user.is_staff = True

        if email and email.lower() in settings.ADMIN_SUPERUSERS:
            user.is_superuser = True

        user.save(update_fields=["email", "is_staff", "is_superuser"])

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return HttpResponseRedirect(reverse("admin:index"))


def jwt_logout(request):
    logout(request)
    return HttpResponseRedirect("/admin/login/")
