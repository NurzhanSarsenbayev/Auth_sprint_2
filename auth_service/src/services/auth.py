from typing import Optional
from uuid import UUID
from fastapi import HTTPException, Response, Request
from http import HTTPStatus

from models import LoginHistory
from utils.security import verify_password
from helpers.auth_helpers import (
    issue_tokens,
    set_refresh_cookie,
    clear_refresh_cookie,
    validate_refresh,
    blacklist_token,
)
from .base import BaseService
from schemas.auth import AuthResult, TokenPair


class AuthService(BaseService):
    # --------- базовые операции ---------
    async def authenticate_user(
        self, username: str, password: str
    ) -> Optional[AuthResult]:
        """Проверка логина/пароля и выдача токенов."""
        user = await self.repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None

        tokens: TokenPair = issue_tokens(user)

        if self.redis:
            await self.redis.sadd(
                f"user_refresh:{user.user_id}", tokens.refresh_token
            )

        return {"user": user, "tokens": tokens}

    async def record_login(
        self, user_id: UUID | str, user_agent: str, ip_address: str
    ):
        """Фиксируем факт входа в историю логинов."""
        login = LoginHistory(user_id=user_id,
                             user_agent=user_agent,
                             ip_address=ip_address)
        self.repo.session.add(login)
        await self.repo.session.commit()

    async def logout(self, user_id: UUID, refresh_token: str):
        """Логаут одного токена."""
        if self.redis:
            await blacklist_token(self.redis, refresh_token)
            await self.redis.srem(f"user_refresh:{user_id}", refresh_token)

    async def logout_all(self, user_id: UUID):
        """Логаут всех refresh-токенов пользователя."""
        if not self.redis:
            return
        tokens = await self.redis.smembers(f"user_refresh:{user_id}")
        for token in tokens:
            token = token.decode() if isinstance(token, bytes) else token
            await blacklist_token(self.redis, token)
        await self.redis.delete(f"user_refresh:{user_id}")

    # --------- сценарии высокого уровня ---------
    async def login_with_form(
        self, username: str,
            password: str,
            request: Request,
            response: Response
    ) -> TokenPair:
        result = await self.authenticate_user(username, password)
        if not result:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail="Invalid credentials")

        user, tokens = result["user"], result["tokens"]

        await self.record_login(
            user.user_id,
            request.headers.get("user-agent", ""),
            request.client.host or "",
        )
        set_refresh_cookie(response, tokens.refresh_token)
        return tokens

    async def login_with_json(self,
                              username: str,
                              password: str) -> TokenPair:
        result = await self.authenticate_user(username, password)
        if not result:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail="Invalid credentials")
        return result["tokens"]

    async def refresh_by_cookie(self,
                                refresh_token: str | None) -> TokenPair:
        user = await validate_refresh(refresh_token,
                                      self.repo.session,
                                      self.redis,
                                      self)
        return issue_tokens(user)

    async def logout_by_cookie(self,
                               refresh_token: str | None,
                               response: Response) -> dict[str, str]:
        if not refresh_token:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                detail="No refresh token")

        user = await validate_refresh(refresh_token,
                                      self.repo.session,
                                      self.redis,
                                      self)
        await self.logout(user.user_id, refresh_token)
        clear_refresh_cookie(response)
        return {"detail": "Logged out successfully"}
