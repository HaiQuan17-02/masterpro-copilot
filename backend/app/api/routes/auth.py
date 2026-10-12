"""
Auth and RBAC Routes for MasterPro Copilot (Week 8).
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth import UserLogin, UserOut, Token, RoleEnum
from app.core.security import DEMO_USERS, create_access_token, get_current_user_optional

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


@router.post("/login", response_model=Token, summary="Đăng nhập nhận JWT Token theo vai trò")
def login(payload: UserLogin):
    user = DEMO_USERS.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(
            status_code=401,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác (Thử: cashier1, inventory1, accountant1, admin / mk: 123)"
        )

    token_str = create_access_token(user)
    return Token(
        access_token=token_str,
        token_type="bearer",
        user=UserOut(
            user_id=user["user_id"],
            username=user["username"],
            full_name=user["full_name"],
            role=user["role"],
            permissions=user["permissions"]
        )
    )


@router.get("/me", response_model=UserOut, summary="Lấy thông tin tài khoản hiện tại")
def get_me(user: UserOut = Depends(get_current_user_optional)):
    if not user:
        # Trả về tài khoản mặc định Cashier nếu chưa đăng nhập
        u = DEMO_USERS["cashier1"]
        return UserOut(
            user_id=u["user_id"],
            username=u["username"],
            full_name=u["full_name"],
            role=u["role"],
            permissions=u["permissions"]
        )
    return user


@router.get("/demo-users", summary="Danh sách tài khoản demo các vai trò trong ERP")
def get_demo_users():
    return [
        {
            "username": u["username"],
            "password": u["password"],
            "full_name": u["full_name"],
            "role": u["role"].value,
            "permissions": u["permissions"]
        }
        for u in DEMO_USERS.values()
    ]
