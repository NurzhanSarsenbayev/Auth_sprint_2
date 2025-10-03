import httpx
from jose import jwt
from django.conf import settings
from django.core.cache import cache


JWKS_CACHE_KEY = "auth:jwks"


async def _fetch_jwks():
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(settings.AUTH_JWKS_URL)
        r.raise_for_status()
        return r.json()


def _get_jwks():
    jwks = cache.get(JWKS_CACHE_KEY)
    if jwks:
        return jwks
    # синхронно — ок для логина (редко)
    import anyio
    jwks = anyio.run(_fetch_jwks)
    cache.set(JWKS_CACHE_KEY, jwks, timeout=int(
        getattr(settings, "CACHE_TTL", 600)))
    return jwks


def _decode(token: str) -> dict:
    jwks = _get_jwks()
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    key = next((k for k in jwks.get("keys", [])
                if k.get("kid") == kid), None)
    if not key:
        raise ValueError("Unknown key id")
    # aud не проверяем
    return jwt.decode(token,
                      key,
                      algorithms=["RS256"],
                      options={"verify_aud": False}
                      )
