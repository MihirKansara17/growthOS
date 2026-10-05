"""
============================================================
MedIntel360
OpenRouter Client

Production-safe LLM client for MedIntel360.

Responsibilities
----------------
• Load OpenRouter configuration.
• Build chat-completion requests.
• Send requests safely.
• Handle API/provider errors.
• Parse valid LLM responses.
• Reject malformed or empty responses.
• Keep provider-specific failures isolated.

Author : Jainam Gada
============================================================
"""

import os

import requests

from dotenv import load_dotenv


# ============================================================
# OPENROUTER CLIENT
# ============================================================

class OpenRouterClient:

    def __init__(self):

        # --------------------------------------------------
        # Load environment variables
        # --------------------------------------------------

        load_dotenv()

        self.api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        self.model = os.getenv(
            "OPENROUTER_MODEL"
        )

        self.base_url = os.getenv(
            "OPENROUTER_BASE_URL"
        )

        self.app_name = os.getenv(
            "APP_NAME",
            "MedIntel360"
        )

        # --------------------------------------------------
        # HTTP Session
        # --------------------------------------------------

        self.session = requests.Session()

        self.session.headers.update({

            "Authorization": (
                f"Bearer {self.api_key}"
            ),

            "Content-Type": "application/json",

            "HTTP-Referer": "http://localhost",

            "X-Title": self.app_name
        })

        # --------------------------------------------------
        # Validate configuration
        # --------------------------------------------------

        self._validate_config()

    # ======================================================
    # CONFIGURATION VALIDATION
    # ======================================================

    def _validate_config(self):

        required = {

            "OPENROUTER_API_KEY": self.api_key,

            "OPENROUTER_MODEL": self.model,

            "OPENROUTER_BASE_URL": self.base_url
        }

        for key, value in required.items():

            if not value:

                raise ValueError(
                    f"{key} not found in .env"
                )

    # ======================================================
    # BUILD PAYLOAD
    # ======================================================

    def _build_payload(
        self,
        system_prompt,
        user_prompt,
        temperature,
        max_tokens
    ):

        return {

            "model": self.model,

            "messages": [

                {
                    "role": "system",

                    "content": system_prompt
                },

                {
                    "role": "user",

                    "content": user_prompt
                }
            ],

            "temperature": temperature,

            "max_tokens": max_tokens
        }

    # ======================================================
    # SEND REQUEST
    # ======================================================

    def _send_request(
        self,
        payload
    ):

        try:

            response = self.session.post(

                self.base_url,

                json=payload,

                timeout=60
            )

        except requests.Timeout as error:

            raise RuntimeError(
                "OpenRouter request timed out."
            ) from error

        except requests.RequestException as error:

            raise RuntimeError(
                f"OpenRouter request failed: {error}"
            ) from error

        # --------------------------------------------------
        # HTTP error handling
        # --------------------------------------------------

        if response.status_code == 429:

            raise RuntimeError(
                "OpenRouter rate limit reached "
                "(HTTP 429). Please retry later."
            )

        if response.status_code == 400:

            try:

                data = response.json()

                message = data.get(
                    "error",
                    {}
                ).get(
                    "message"
                )

            except ValueError:

                message = None

            if message:

                raise RuntimeError(
                    f"OpenRouter rejected the request: "
                    f"{message}"
                )

            raise RuntimeError(
                "OpenRouter rejected the request "
                "(HTTP 400)."
            )

        if response.status_code == 502:

            raise RuntimeError(
                "OpenRouter provider is temporarily "
                "unavailable (HTTP 502)."
            )

        if response.status_code >= 500:

            raise RuntimeError(
                "OpenRouter provider returned a "
                f"server error (HTTP {response.status_code})."
            )

        if not response.ok:

            raise RuntimeError(
                "OpenRouter request failed "
                f"(HTTP {response.status_code})."
            )

        return response

    # ======================================================
    # PARSE RESPONSE
    # ======================================================

    def _parse_response(
        self,
        response
    ):

        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------

        try:

            data = response.json()

        except ValueError as error:

            raise RuntimeError(
                "OpenRouter returned invalid JSON."
            ) from error

        # --------------------------------------------------
        # Handle API-level error object
        # --------------------------------------------------

        if "error" in data:

            error_data = data.get(
                "error"
            )

            if isinstance(
                error_data,
                dict
            ):

                message = error_data.get(
                    "message",
                    "Unknown OpenRouter error."
                )

            else:

                message = str(
                    error_data
                )

            raise RuntimeError(
                f"OpenRouter error: {message}"
            )

        # --------------------------------------------------
        # Validate choices
        # --------------------------------------------------

        choices = data.get(
            "choices"
        )

        if not choices:

            raise RuntimeError(
                "OpenRouter response did not "
                "contain any choices."
            )

        # --------------------------------------------------
        # Validate first choice
        # --------------------------------------------------

        first_choice = choices[0]

        if not isinstance(
            first_choice,
            dict
        ):

            raise RuntimeError(
                "OpenRouter returned an invalid "
                "choice object."
            )

        message = first_choice.get(
            "message"
        )

        if not isinstance(
            message,
            dict
        ):

            raise RuntimeError(
                "OpenRouter response did not "
                "contain a valid message."
            )

        # --------------------------------------------------
        # Extract content
        # --------------------------------------------------

        content = message.get(
            "content"
        )

        # Some reasoning models/providers may return
        # no content when the generation is truncated.
        if content is None:

            finish_reason = first_choice.get(
                "finish_reason"
            )

            if finish_reason == "length":

                raise RuntimeError(
                    "LLM response was truncated "
                    "before producing an answer."
                )

            raise RuntimeError(
                "LLM returned no answer content."
            )

        content = str(
            content
        ).strip()

        if not content:

            raise RuntimeError(
                "LLM returned an empty answer."
            )

        return content

    # ======================================================
    # CHAT
    # ======================================================

    def chat(
        self,
        system_prompt,
        user_prompt,
        temperature=0.2,
        max_tokens=1000
    ):

        # --------------------------------------------------
        # Basic input validation
        # --------------------------------------------------

        if not isinstance(
            system_prompt,
            str
        ):

            raise TypeError(
                "system_prompt must be a string."
            )

        if not isinstance(
            user_prompt,
            str
        ):

            raise TypeError(
                "user_prompt must be a string."
            )

        if not system_prompt.strip():

            raise ValueError(
                "system_prompt cannot be empty."
            )

        if not user_prompt.strip():

            raise ValueError(
                "user_prompt cannot be empty."
            )

        if max_tokens <= 0:

            raise ValueError(
                "max_tokens must be greater than zero."
            )

        # --------------------------------------------------
        # Build request
        # --------------------------------------------------

        payload = self._build_payload(

            system_prompt,

            user_prompt,

            temperature,

            max_tokens
        )

        # --------------------------------------------------
        # Send request
        # --------------------------------------------------

        response = self._send_request(
            payload
        )

        # --------------------------------------------------
        # Parse response
        # --------------------------------------------------

        return self._parse_response(
            response
        )