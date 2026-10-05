from sqlalchemy.orm import Session
from app.ai.engine.llm_client import LLMClient
from app.ai.engine.metadata_manager import MetadataManager
from app.ai.engine.conversation_manager import ConversationManager
from app.ai.engine.data_understanding_agent import DataUnderstandingAgent
from app.ai.engine.parameter_validator import ParameterValidator
from app.ai.engine.engine_executor import EngineExecutor
from app.ai.engine.insight_generator import InsightGenerator

class QueryEngine:
    def __init__(self, metadata_dir: str = None):
        self.llm = LLMClient()
        self.metadata = MetadataManager(metadata_dir)
        self.conversation = ConversationManager()
        
        self.understanding_agent = DataUnderstandingAgent(self.metadata, self.conversation, self.llm)
        self.validator = ParameterValidator(self.metadata)
        self.executor = EngineExecutor()
        self.insight_generator = InsightGenerator(self.llm)

    def ask(self, db: Session, tenant_id: str, query: str) -> dict:
        """
        Orchestrates the Text-to-Tool pipeline.
        Returns a dict suitable for the API response.
        """
        if not query or not query.strip():
            return {"answer": "Query cannot be empty.", "success": False}

        # 1. Data Understanding (Intent & Tool Selection)
        try:
            understanding_result = self.understanding_agent.understand(query)
        except Exception as e:
            return {"answer": f"Failed to understand query: {str(e)}", "success": False}

        if understanding_result.requires_clarification:
            return {
                "answer": understanding_result.clarification_question or "Could you please clarify your question?",
                "success": True,
                "mode": "CLARIFICATION"
            }

        # 2. Parameter Validation
        is_valid, err_msg, validated_args = self.validator.validate(understanding_result)
        if not is_valid:
            return {"answer": err_msg, "success": False, "mode": "VALIDATION_ERROR"}

        # 3. Engine Execution
        success, raw_data, err_msg = self.executor.execute(
            db=db, 
            tenant_id=tenant_id, 
            selected_tool=understanding_result.selected_tool,
            validated_args=validated_args
        )

        if not success:
            return {"answer": err_msg, "success": False, "mode": "EXECUTION_ERROR"}

        # 4. Insight Generation
        insight = self.insight_generator.generate(
            query=query, 
            selected_tool=understanding_result.selected_tool, 
            raw_data=raw_data
        )

        # 5. Save to DB
        self.conversation.save_interaction_to_db(
            db=db,
            tenant_id=tenant_id,
            user_query=query,
            ai_response=insight,
            selected_tool=understanding_result.selected_tool
        )

        return {
            "answer": insight,
            "success": True,
            "mode": "TEXT_TO_TOOL",
            "tool_used": understanding_result.selected_tool,
            "raw_data": raw_data
        }
