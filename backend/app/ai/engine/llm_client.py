import requests
import json
from app.core.config import settings

class LLMClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.0, max_tokens: int = 800) -> str:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://growthos-retail.com",
            "X-Title": "GrowthOS Retail Intelligence"
        }

        payload = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        # OpenRouter Fallback Support: If multiple models are comma-separated, pass as an array.
        if "," in self.model:
            payload["models"] = [m.strip() for m in self.model.split(",")]
        else:
            payload["model"] = self.model

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"LLM API request failed: {e}. Details: {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"LLM API request failed: {e}")
