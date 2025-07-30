from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class IdMixin(BaseModel):
    id: str = Field(alias='_id')


class UpdatedAtMixin(BaseModel):
    updatedAt: Optional[datetime] = Field(None, alias='_updatedAt')


class TypeMixin(BaseModel):
    type: str


class UserModel(IdMixin, TypeMixin, UpdatedAtMixin):
    active: bool
    aliasId: str
    createdAt: str
    domain: str
    name: str
    notificationsDisabled: bool = False
    preferences: List = []
    roles: List[str]
    username: str


class AdminBotModel(IdMixin, TypeMixin, UpdatedAtMixin):
    active: bool
    createdAt: str
    name: str
    notificationsDisabled: bool = False
    preferences: List = []
    roles: List[str]
    username: str


class AuthData(BaseModel):
    userId: str
    authToken: str
    authTokenExpires: int
    me: UserModel | AdminBotModel


class AuthResponse(BaseModel):
    status: str
    data: AuthData
