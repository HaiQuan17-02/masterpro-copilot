"""
Schemas for Authentication and RBAC (Week 8).
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class RoleEnum(str, Enum):
    CASHIER = "cashier"         # Thu ngân POS
    INVENTORY = "inventory"     # Thủ kho
    ACCOUNTANT = "accountant"   # Kế toán viên
    ADMIN = "admin"             # Quản trị viên


class UserLogin(BaseModel):
    username: str = Field(..., description="Tên đăng nhập")
    password: str = Field(..., description="Mật khẩu")


class UserOut(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: RoleEnum
    permissions: List[str]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
