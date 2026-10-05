import json
from dataclasses import dataclass, field
from typing import Any, List, Optional
from app.ai.engine.metadata_manager import MetadataManager
from app.ai.engine.conversation_manager import ConversationManager
from app.ai.engine.llm_client import LLMClient

@dataclass
class DataUnderstandingResult:
    query: str
    selected_tool: Optional[str] = None
    timeframe: Optional[str] = None
    filters: List[dict] = field(default_factory=list)
    requires_clarification: bool = False
    clarification_question: Optional[str] = None

class DataUnderstandingAgent:
    def __init__(self, metadata: MetadataManager, conversation: ConversationManager, llm: LLMClient):
        self.metadata = metadata
        self.conversation = conversation
        self.llm = llm

    def understand(self, query: str) -> DataUnderstandingResult:
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty.")

        context = self.conversation.get_context()
        glossary_matches = self.metadata.search_glossary(query)
        tools = self.metadata.get_tools()

        system_prompt = """
        You are GrowthOS, an AI decision intelligence assistant for retail.
        Your task is to map the user's query to one of the approved analytical tools.
        
        RULES:
        1. Select EXACTLY ONE tool from the AVAILABLE TOOLS list.
        2. If the user's query is ambiguous and doesn't match any tool, set requires_clarification=true and provide a clarification_question.
        3. Extract any mentioned timeframe (e.g., 'last week', 'this month'). If none, leave it null.
        4. Extract any filters mentioned (e.g., specific store, category).
        5. Use the GLOSSARY MATCHES to translate user slang into the correct tool intent.
        6. If this is a follow-up query, consider the PREVIOUS CONTEXT.
        
        Output valid JSON only. Format:
        {
            "selected_tool": "string or null",
            "timeframe": "string or null",
            "filters": [{"dimension": "string", "value": "string"}],
            "requires_clarification": false,
            "clarification_question": "string or null"
        }
        """

        user_prompt = f"""
        CURRENT USER QUERY:
        {query}

        PREVIOUS CONTEXT (if follow-up):
        {json.dumps(context)}

        GLOSSARY MATCHES (Found in query):
        {json.dumps(glossary_matches)}

        AVAILABLE TOOLS:
        {json.dumps(tools)}
        """

        try:
            response = self.llm.chat(system_prompt=system_prompt, user_prompt=user_prompt)
            # Clean possible markdown block
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            data = json.loads(response.strip())

            result = DataUnderstandingResult(
                query=query,
                selected_tool=data.get("selected_tool"),
                timeframe=data.get("timeframe"),
                filters=data.get("filters", []),
                requires_clarification=data.get("requires_clarification", False),
                clarification_question=data.get("clarification_question")
            )
            
            # Update context if a tool was successfully chosen
            if result.selected_tool:
                self.conversation.update_context(
                    selected_tool=result.selected_tool,
                    timeframe=result.timeframe,
                    filters=result.filters
                )

            return result

        except Exception as e:
            raise RuntimeError(f"Data understanding failed: {e}")
