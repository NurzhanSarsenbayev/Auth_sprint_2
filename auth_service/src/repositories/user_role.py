from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from schemas.role import RoleResponse
from schemas.user_role import UserRoleListResponse
from models import User, Role, UserRole


class UserRoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_role_to_user(self, user_id: UUID, role_id: UUID) -> UserRole:
        """Просто добавляет связь (без commit), возвращает объект."""
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        await self.session.flush()  # получаем PK
        return user_role

    async def assign_role(self, user_id: UUID, role_id: UUID) -> UserRole:
        """Назначает роль пользователю, если её ещё нет (commit внутри)."""
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        )
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            return existing  # уже есть

        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        await self.session.commit()
        await self.session.refresh(user_role)
        return user_role

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID):
        query = delete(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        )
        result = await self.session.execute(query)
        return result  # вернём result, чтобы .rowcount можно было проверить

    async def get_roles_for_user(self, user_id: UUID) -> List[Role]:
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.role_id)
            .where(UserRole.user_id == user_id)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_user_role_entry(self, user_id: UUID,
                                  role_id: UUID) -> Optional[UserRole]:
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_all(self) -> List[UserRoleListResponse]:
        """Возвращает всех пользователей и их роли (ORM → Pydantic)."""
        query = (
            select(User)
            .options(
                selectinload(User.user_roles).selectinload(UserRole.role)
            )
        )
        result = await self.session.execute(query)
        users = result.scalars().all()

        return [
            UserRoleListResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                hashed_password=user.hashed_password,
                roles=[
                    RoleResponse(
                        role_id=ur.role.role_id,
                        name=ur.role.name,
                        description=ur.role.description
                    )
                    for ur in user.user_roles if ur.role
                ]
            )
            for user in users
        ]
