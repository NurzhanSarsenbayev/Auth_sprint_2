import httpx
from urllib.parse import quote
from typing import Optional

from core.config import settings
from core.oauth.interfaces import OAuthProvider
from core.oauth.types import OAuthUserInfo

YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
YANDEX_USERINFO_URL = "https://login.yandex.ru/info"


class YandexOAuthProvider(OAuthProvider):
    name = "yandex"

    def get_authorize_url(self, state: Optional[str] = None) -> str:
        redirect = quote(settings.yandex_redirect_uri, safe="")
        base = (
            f"{YANDEX_AUTH_URL}"
            f"?response_type=code"
            f"&client_id={settings.yandex_client_id}"
            f"&redirect_uri={redirect}"
        )
        if state:
            base += f"&state={state}"
        # при желании можно попросить подтверждение каждый раз:
        # base += "&force_confirm=yes"
        return base

    async def exchange_code_for_token(self, code: str) -> str:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                YANDEX_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.yandex_client_id,
                    "client_secret": settings.yandex_client_secret,
                },
            )
        resp.raise_for_status()
        return resp.json()["access_token"]

    async def get_userinfo(self, access_token: str) -> OAuthUserInfo:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                YANDEX_USERINFO_URL,
                params={"format": "json"},
                headers={"Authorization": f"OAuth {access_token}"},
            )
        resp.raise_for_status()
        data = resp.json()
        return OAuthUserInfo(
            provider=self.name,
            provider_account_id=str(data["id"]),
            email=data.get("default_email"),
            login=data.get("login"),
            name=data.get("real_name"),
        )
