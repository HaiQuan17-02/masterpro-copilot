"""
Service managing Feedback and Escalation Tickets (Week 7).
"""

import os
import json
import uuid
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.schemas.feedback import FeedbackCreate, FeedbackItem, FeedbackStats, EscalationCreate, EscalationTicket


class FeedbackService:
    def __init__(self, data_dir: str = "backend/app/data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.feedback_file = os.path.join(self.data_dir, "feedbacks.json")
        self.escalation_file = os.path.join(self.data_dir, "escalation_tickets.json")
        self._lock = threading.Lock()

        self._feedbacks: List[Dict[str, Any]] = self._load_json(self.feedback_file)
        self._escalations: List[Dict[str, Any]] = self._load_json(self.escalation_file)

    def _load_json(self, path: str) -> List[Dict[str, Any]]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_json(self, path: str, data: List[Dict[str, Any]]):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save {path}: {e}")

    def add_feedback(self, payload: FeedbackCreate) -> Dict[str, Any]:
        with self._lock:
            feedback_id = f"fb_{uuid.uuid4().hex[:8]}"
            now_iso = datetime.now().isoformat()
            item = {
                "feedback_id": feedback_id,
                "message_id": payload.message_id,
                "rating": payload.rating.lower(),
                "reason": payload.reason,
                "comment": payload.comment,
                "cited_doc_ids": payload.cited_doc_ids or [],
                "query": payload.query,
                "created_at": now_iso
            }
            self._feedbacks.append(item)
            self._save_json(self.feedback_file, self._feedbacks)
            return item

    def get_stats(self) -> FeedbackStats:
        with self._lock:
            total = len(self._feedbacks)
            likes = sum(1 for f in self._feedbacks if f["rating"] == "like")
            dislikes = sum(1 for f in self._feedbacks if f["rating"] == "dislike")
            helpful_rate = round((likes / total * 100), 1) if total > 0 else 100.0

            reasons: Dict[str, int] = {}
            for f in self._feedbacks:
                r = f.get("reason")
                if r:
                    reasons[r] = reasons.get(r, 0) + 1

            return FeedbackStats(
                total=total,
                likes=likes,
                dislikes=dislikes,
                helpful_rate_percent=helpful_rate,
                reason_breakdown=reasons
            )

    def create_escalation(self, payload: EscalationCreate) -> EscalationTicket:
        with self._lock:
            ticket_id = f"ESC-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
            now_iso = datetime.now().isoformat()
            item = {
                "ticket_id": ticket_id,
                "query": payload.query,
                "bot_response": payload.bot_response,
                "conversation_id": payload.conversation_id,
                "user_note": payload.user_note,
                "priority": payload.priority.lower(),
                "status": "pending",
                "user_role": payload.user_role or "cashier",
                "retrieved_chunks_count": len(payload.retrieved_chunks or []),
                "created_at": now_iso,
                "updated_at": now_iso,
                "raw_chunks": payload.retrieved_chunks or []
            }
            self._escalations.append(item)
            self._save_json(self.escalation_file, self._escalations)

            return EscalationTicket(
                ticket_id=ticket_id,
                query=item["query"],
                bot_response=item["bot_response"],
                conversation_id=item["conversation_id"],
                user_note=item["user_note"],
                priority=item["priority"],
                status=item["status"],
                user_role=item["user_role"],
                retrieved_chunks_count=item["retrieved_chunks_count"],
                created_at=item["created_at"],
                updated_at=item["updated_at"]
            )

    def list_escalations(self, status: Optional[str] = None) -> List[EscalationTicket]:
        with self._lock:
            res = []
            for item in reversed(self._escalations):
                if status and item.get("status") != status:
                    continue
                res.append(EscalationTicket(
                    ticket_id=item["ticket_id"],
                    query=item["query"],
                    bot_response=item["bot_response"],
                    conversation_id=item.get("conversation_id"),
                    user_note=item.get("user_note"),
                    priority=item["priority"],
                    status=item["status"],
                    user_role=item["user_role"],
                    retrieved_chunks_count=item.get("retrieved_chunks_count", 0),
                    created_at=item["created_at"],
                    updated_at=item["updated_at"]
                ))
            return res

    def update_escalation_status(self, ticket_id: str, new_status: str) -> Optional[EscalationTicket]:
        with self._lock:
            for item in self._escalations:
                if item["ticket_id"] == ticket_id:
                    item["status"] = new_status
                    item["updated_at"] = datetime.now().isoformat()
                    self._save_json(self.escalation_file, self._escalations)
                    return EscalationTicket(
                        ticket_id=item["ticket_id"],
                        query=item["query"],
                        bot_response=item["bot_response"],
                        conversation_id=item.get("conversation_id"),
                        user_note=item.get("user_note"),
                        priority=item["priority"],
                        status=item["status"],
                        user_role=item["user_role"],
                        retrieved_chunks_count=item.get("retrieved_chunks_count", 0),
                        created_at=item["created_at"],
                        updated_at=item["updated_at"]
                    )
            return None


# Global singleton
_service_instance: Optional[FeedbackService] = None

def get_feedback_service() -> FeedbackService:
    global _service_instance
    if _service_instance is None:
        _service_instance = FeedbackService()
    return _service_instance
