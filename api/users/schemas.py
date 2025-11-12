from enum import Enum
from typing import Optional, List

from ninja import Schema

from base.schemas import BaseOut, BaseQuery


class UserType(str, Enum):
    ADMIN = 'admin'
    MISSIONER = 'missioner'
    STAFF = 'staff'
    EXEC = 'exec'


class RoleQuery(BaseQuery):
    name: Optional[str] = None


class RoleSchema(BaseOut):
    name: str
    description: str
    permissions: list[str]


class UserFilterSchema(BaseQuery):
    search: Optional[str] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


class UserCreate(Schema):
    email: str
    first_name: str | None = None
    last_name: str | None = None
    password: str
    profile_photo: str | None = None
    preferred_username: str | None = None
    role_id: int | None = None
    permissions: list[str] | None = None
    role_name: str | None = None
    user_type: Optional[UserType] = None


class RoleCreate(Schema):
    name: str
    description: Optional[str] = ''
    permissions: list[str]


class RoleOut(Schema):
    id: int
    name: str
    description: str
    permissions: list[str]


class PermissionQuery(Schema):
    user_type: Optional[UserType] = None
