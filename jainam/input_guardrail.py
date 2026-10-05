"""
============================================================
MedIntel360
Input Guardrail

Validates and sanitizes user queries before they reach
the AI query-understanding pipeline.

Author : Jainam Gada
============================================================
"""


class InputGuardrail:

    # ========================================================
    # Configuration
    # ========================================================

    MAX_QUERY_LENGTH = 1000

    # Obvious prompt-injection / instruction-manipulation
    # patterns. This is intentionally conservative.
    BLOCKED_PATTERNS = (

        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore your instructions",
        "disregard previous instructions",
        "disregard all previous instructions",

        "forget previous instructions",
        "forget all previous instructions",

        "system prompt",
        "reveal your prompt",
        "show me your prompt",
        "show your system prompt",

        "developer message",
        "developer instructions",

        "jailbreak",
        "bypass your restrictions",
        "bypass your rules",

    )

    # ========================================================
    # Main Validation
    # ========================================================

    def validate(self, query: str) -> dict:

        # ----------------------------------------------------
        # Type validation
        # ----------------------------------------------------

        if not isinstance(query, str):

            return self._blocked(
                "Query must be a string."
            )

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        query = query.strip()

        # ----------------------------------------------------
        # Empty query
        # ----------------------------------------------------

        if not query:

            return self._blocked(
                "Query cannot be empty."
            )

        # ----------------------------------------------------
        # Length protection
        # ----------------------------------------------------

        if len(query) > self.MAX_QUERY_LENGTH:

            return self._blocked(
                "Query exceeds the maximum allowed length."
            )

        # ----------------------------------------------------
        # Prompt injection detection
        # ----------------------------------------------------

        normalized = " ".join(
            query.lower().split()
        )

        for pattern in self.BLOCKED_PATTERNS:

            if pattern in normalized:

                return self._blocked(
                    "Query contains a blocked instruction pattern."
                )

        # ----------------------------------------------------
        # Valid
        # ----------------------------------------------------

        return {
            "allowed": True,
            "query": query,
            "reason": None
        }

    # ========================================================
    # Helpers
    # ========================================================

    @staticmethod
    def _blocked(reason):

        return {
            "allowed": False,
            "query": None,
            "reason": reason
        }