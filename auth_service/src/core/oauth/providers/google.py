import httpx
from urllib.parse import quote
from typing import Optional

from core.config import settings
from core.oauth.interfaces import OAuthProvider
from core.oauth.types import OAuthUserInfo

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleOAuthProvider(OAuthProvider):
    name = "google"

    def get_authorize_url(self, state: Optional[str] = None) -> str:
        redirect = quote(settings.google_redirect_uri, safe="")
        base = (
            f"{GOOGLE_AUTH_URL}"
            f"?response_type=code"
            f"&client_id={settings.google_client_id}"
            f"&redirect_uri={redirect}"
            f"&scope=openid%20email%20profile"
        )
        if state:
            base += f"&state={state}"
        return base

    async def exchange_code_for_token(self, code: str) -> str:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                },
            )
        resp.raise_for_status()
        return resp.json()["access_token"]

    async def get_userinfo(self, access_token: str) -> OAuthUserInfo:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        resp.raise_for_status()
        data = resp.json()
        return OAuthUserInfo(
            provider=self.name,
            provider_account_id=data["sub"],  # уникальный ID Google
            email=data.get("email"),
            login=data.get("email"),  # у Google логин ≈ email
            name=data.get("name"),
        )
