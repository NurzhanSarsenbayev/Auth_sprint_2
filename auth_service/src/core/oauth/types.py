from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class OAuthUserInfo:
    provider: str                # "yandex"
    provider_account_id: str     # уникальный ID у провайдера (data["id"])
    email: str | None
    login: str | None
    name: str | None = None
