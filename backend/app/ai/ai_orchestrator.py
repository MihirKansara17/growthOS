from sqlalchemy.orm import Session
from app.ai.engine.query_engine import QueryEngine

# We keep a single instance in memory to preserve conversation context across API calls
# In a real multi-user app, this would be keyed by user_id or tenant_id.
_engine_instance = QueryEngine()

class AIOrchestrator:
    @staticmethod
    def ask_growthos(db: Session, tenant_id: str, prompt: str):
        """
        Entry point for the API router.
        Delegates the natural language query to the Text-to-Tool QueryEngine pipeline.
        """
        # Call the new pipeline
        result = _engine_instance.ask(db=db, tenant_id=tenant_id, query=prompt)
        
        return result
