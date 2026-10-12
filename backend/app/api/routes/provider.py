"""
API Endpoints for Hybrid Provider Management and Circuit Breaker (Week 10).
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from ai.providers.hybrid_manager import HybridProviderManager

router = APIRouter(prefix="/provider", tags=["Hybrid AI Provider & Circuit Breaker"])


class ModeSwitchRequest(BaseModel):
    mode: str = Field(..., description="'auto', 'online_preferred', 'offline_only'")


class SimulateFailureRequest(BaseModel):
    simulate_failure: bool = Field(..., description="Bật/tắt giả lập mất kết nối mạng Cloud")


@router.get("/status", summary="Lấy thông tin trạng thái hoạt động của Hybrid AI Engine")
def get_provider_status() -> Dict[str, Any]:
    manager = HybridProviderManager.get_instance()
    return manager.get_status()


@router.post("/mode", summary="Chuyển đổi chế độ hoạt động (Auto, Online Preferred, Offline Only)")
def switch_mode(payload: ModeSwitchRequest) -> Dict[str, Any]:
    manager = HybridProviderManager.get_instance()
    try:
        manager.set_mode(payload.mode)
        return {
            "status": "success",
            "message": f"Đã chuyển sang chế độ {payload.mode}",
            "current_mode": manager.mode
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/simulate-failure", summary="Giả lập mất kết nối mạng Cloud AI (Kiểm thử UAT)")
def simulate_failure(payload: SimulateFailureRequest) -> Dict[str, Any]:
    manager = HybridProviderManager.get_instance()
    manager.online_provider.set_simulate_failure(payload.simulate_failure)
    return {
        "status": "success",
        "simulate_failure": payload.simulate_failure,
        "message": "Đã " + ("bật" if payload.simulate_failure else "tắt") + " chế độ giả lập lỗi mạng Cloud LLM"
    }
