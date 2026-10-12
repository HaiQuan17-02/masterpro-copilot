import sys
import os
import time
from typing import List, Dict, Any, Optional

# Ensure ai module is accessible
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ai_dir = os.path.join(backend_dir, "..", "ai")
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from qdrant_manager import QdrantVectorStore


class SearchService:
    """
    Search Service wrapping QdrantVectorStore for FastAPI backend.
    """
    _instance: Optional["SearchService"] = None

    def __init__(self):
        storage_path = os.path.join(ai_dir, "qdrant_storage")
        self.store = QdrantVectorStore.get_shared_instance(storage_path=storage_path)

    @classmethod
    def get_instance(cls) -> "SearchService":
        if cls._instance is None:
            cls._instance = SearchService()
        return cls._instance

    # RBAC Role to Module mapping
    ROLE_MODULE_MAPPING = {
        "admin": None,  # Toàn quyền
        "cashier": ["bán hàng", "pos", "hóa đơn", "máy in", "kết số", "khách hàng", "đăng nhập", "chung", "hệ thống"],
        "inventory": ["kho hàng", "kiểm kê", "nhập xuất", "chuyển kho", "nhà cung cấp", "hàng hóa", "đăng nhập", "chung"],
        "accountant": ["sổ quỹ", "tài chính", "kế toán", "báo cáo", "thuế", "doanh thu", "công nợ", "đăng nhập", "chung"]
    }

    def search(
        self,
        query: str,
        limit: int = 3,
        score_threshold: float = 0.30,
        category: Optional[str] = None,
        module: Optional[str] = None,
        user_role: Optional[str] = None
    ) -> Dict[str, Any]:
        start_t = time.perf_counter()
        hits = self.store.search(
            query=query,
            limit=limit if not user_role or user_role == "admin" else limit + 5,
            score_threshold=score_threshold,
            category=category,
            module=module
        )

        # Apply RBAC filtering
        filtered_hits = []
        if user_role and user_role.lower() != "admin":
            allowed_keywords = self.ROLE_MODULE_MAPPING.get(user_role.lower(), [])
            for h in hits:
                h_mod = (h.get("module") or "").lower()
                h_title = (h.get("title") or "").lower()
                h_path = (h.get("heading_path") or "").lower()

                # Check if document matches allowed modules
                is_allowed = any(
                    kw in h_mod or kw in h_title or kw in h_path
                    for kw in allowed_keywords
                )
                if is_allowed:
                    filtered_hits.append(h)
            hits = filtered_hits[:limit]

        latency_ms = round((time.perf_counter() - start_t) * 1000, 2)

        return {
            "query": query,
            "user_role": user_role or "all",
            "total": len(hits),
            "results": hits,
            "latency_ms": latency_ms
        }

    def get_available_filters(self) -> Dict[str, List[str]]:
        return {
            "categories": ["HDSD", "RUNBOOK_L1", "FAQ"],
            "modules": [
                "Đăng nhập", "Hệ thống", "Kho hàng", "Sổ quỹ",
                "Cửa hàng", "Tài khoản", "Sản phẩm", "Khách hàng",
                "Mua hàng", "Bán hàng", "Hardware_POS"
            ]
        }
