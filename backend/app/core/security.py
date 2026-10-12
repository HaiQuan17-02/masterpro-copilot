"""
Security, Mock JWT Authentication and Role-Based Access Control (Week 8).
"""

import hmac
import hashlib
import base64
import json
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.auth import UserOut, RoleEnum

SECRET_KEY = "masterpro-copilot-secret-key-super-secure"
security_scheme = HTTPBearer(auto_error=False)

# Demo User Directory for MasterPro ERP Roles
DEMO_USERS = {
    "cashier1": {
        "user_id": "usr_c01",
        "username": "cashier1",
        "password": "123",
        "full_name": "Nguyễn Văn Thu (Thu ngân POS)",
        "role": RoleEnum.CASHIER,
        "permissions": ["pos_sales", "print_receipt", "close_shift"]
    },
    "inventory1": {
        "user_id": "usr_i01",
        "username": "inventory1",
        "password": "123",
        "full_name": "Trần Kho Vận (Thủ kho)",
        "role": RoleEnum.INVENTORY,
        "permissions": ["inventory_check", "stock_in", "stock_out", "warehouse_transfer"]
    },
    "accountant1": {
        "user_id": "usr_a01",
        "username": "accountant1",
        "password": "123",
        "full_name": "Lê Thị Kế (Kế toán)",
        "role": RoleEnum.ACCOUNTANT,
        "permissions": ["general_ledger", "financial_report", "tax_declare", "debt_management"]
    },
    "admin": {
        "user_id": "usr_admin",
        "username": "admin",
        "password": "admin123",
        "full_name": "Quản Trị Viên Hệ Thống",
        "role": RoleEnum.ADMIN,
        "permissions": ["all_access", "manage_users", "system_settings", "reindex_kb"]
    }
}


def create_access_token(user: Dict[str, Any], expires_delta: int = 86400) -> str:
    """Sinh token định dạng JWT gọn nhẹ HMAC-SHA256."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user["username"],
        "user_id": user["user_id"],
        "role": user["role"].value if isinstance(user["role"], RoleEnum) else str(user["role"]),
        "full_name": user["full_name"],
        "exp": int(time.time()) + expires_delta
    }
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(
        SECRET_KEY.encode(),
        f"{encoded_header}.{encoded_payload}".encode(),
        hashlib.sha256
    ).digest()
    encoded_sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{encoded_header}.{encoded_payload}.{encoded_sig}"


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Giải mã và kiểm tra tính hợp lệ của token."""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    encoded_header, encoded_payload, signature = parts
    expected_sig = base64.urlsafe_b64encode(
        hmac.new(
            SECRET_KEY.encode(),
            f"{encoded_header}.{encoded_payload}".encode(),
            hashlib.sha256
        ).digest()
    ).decode().rstrip("=")

    if not hmac.compare_digest(signature, expected_sig):
        return None

    # Decode payload with padding correction
    rem = len(encoded_payload) % 4
    if rem > 0:
        encoded_payload += "=" * (4 - rem)
    try:
        payload_data = json.loads(base64.urlsafe_b64decode(encoded_payload).decode())
        if payload_data.get("exp", 0) < time.time():
            return None
        return payload_data
    except Exception:
        return None


def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    x_user_role: Optional[str] = Header(None)
) -> Optional[UserOut]:
    """
    Trích xuất User hiện tại từ JWT Bearer token hoặc Header X-User-Role giả lập.
    Nếu không có, mặc định trả về vai trò Cashier hoặc None.
    """
    if auth and auth.credentials:
        payload = verify_token(auth.credentials)
        if payload:
            uname = payload.get("sub")
            if uname in DEMO_USERS:
                u = DEMO_USERS[uname]
                return UserOut(
                    user_id=u["user_id"],
                    username=u["username"],
                    full_name=u["full_name"],
                    role=u["role"],
                    permissions=u["permissions"]
                )

    # Fallback qua X-User-Role (tiện lợi cho frontend test nhanh giữa các tab)
    if x_user_role:
        for u in DEMO_USERS.values():
            if u["role"].value == x_user_role.lower():
                return UserOut(
                    user_id=u["user_id"],
                    username=u["username"],
                    full_name=u["full_name"],
                    role=u["role"],
                    permissions=u["permissions"]
                )

    return None
