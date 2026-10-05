import json
from typing import Any
from app.ai.engine.llm_client import LLMClient

class InsightGenerator:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, query: str, selected_tool: str, raw_data: Any) -> str:
        """
        Takes the raw JSON output from a deterministic engine and turns it into a natural language insight.
        """
        system_prompt = """
        You are GrowthOS, an AI decision intelligence assistant for Indian retail businesses.
        You have just executed an analytical tool to answer the user's query.
        
        RULES:
        1. Base your answer STRICTLY on the RAW DATA provided below. Do not invent any numbers.
        2. Format your answer nicely (use markdown, bullet points, or bold text for emphasis).
        3. Explain what the data means for the business. Don't just regurgitate the JSON.
        4. If the data implies a problem (e.g., stockout risk, revenue drop), recommend a basic retail action based on the data.
        5. Do not hallucinate data that isn't there. If the data is empty, say so.
        """

        user_prompt = f"""
        USER QUERY: 
        {query}
        
        ANALYTICAL TOOL USED: 
        {selected_tool}
        
        RAW DATA (Source of Truth):
        {json.dumps(raw_data)}
        """

        try:
            response = self.llm.chat(system_prompt=system_prompt, user_prompt=user_prompt)
            return response
        except Exception as e:
            return f"I was able to run the analysis, but encountered an error generating the final explanation: {e}"
