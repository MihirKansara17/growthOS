import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import AIChatHistory

class ConversationManager:
    def __init__(self):
        # In-memory history for quick LLM context building
        self.history: List[Dict[str, str]] = []
        
        # Structured context extracted from previous queries
        self.context: Dict[str, Any] = self._default_context()

    def _default_context(self) -> Dict[str, Any]:
        return {
            "selected_tool": None,
            "timeframe": None,
            "filters": []
        }

    def add_message(self, role: str, content: str):
        if role not in ("user", "assistant", "system"):
            raise ValueError(f"Invalid role '{role}'.")
        self.history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return self.history

    def clear_history(self):
        self.history.clear()

    def update_context(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.context:
                raise KeyError(f"'{key}' is not a valid context field.")
            self.context[key] = value

    def get_context(self) -> Dict[str, Any]:
        return self.context

    def clear_context(self):
        self.context = self._default_context()

    def reset(self):
        self.clear_history()
        self.clear_context()

    def save_interaction_to_db(self, db: Session, tenant_id: str, user_query: str, ai_response: str, selected_tool: Optional[str] = None):
        """Persist the chat interaction to the database for audit/analytics."""
        chat_record = AIChatHistory(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_query=user_query,
            ai_response=ai_response,
            selected_tool=selected_tool
        )
        db.add(chat_record)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Failed to save chat history: {e}")
