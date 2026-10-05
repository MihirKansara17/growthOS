"""
============================================================
MedIntel360
Conversation Manager

Maintains conversation history and structured query context
for the AI Engine.

Author : Jainam
============================================================
"""


class ConversationManager:

    def __init__(self):

        # --------------------------------------------------
        # Chat History
        # --------------------------------------------------
        self.history = []

        # --------------------------------------------------
        # Structured Conversation Context
        # --------------------------------------------------
        

        self.context = self._default_context()

    # --------------------------------------------------
    # Default Conversation Context
    # --------------------------------------------------

    def _default_context(self):

        return {

            "selected_dataset": None,

            "dataset_confidence": None,

            "metrics": [],

            "dimensions": [],

            "filters": [],

            "group_by": [],

            "sort_by": None,

            "limit": None,

            "last_sql": None,

            "last_result": None
        }

    # --------------------------------------------------
    # Add Message
    # --------------------------------------------------

    def add_message(self, role, content):

        if role not in ("user", "assistant", "system"):
            raise ValueError(
                f"Invalid role '{role}'. "
                "Expected 'user', 'assistant', or 'system'."
            )

        self.history.append({

            "role": role,

            "content": content

        })

    # --------------------------------------------------
    # Get Conversation History
    # --------------------------------------------------

    def get_history(self):

        return self.history

    # --------------------------------------------------
    # Clear History
    # --------------------------------------------------

    def clear_history(self):

        self.history.clear()

    # --------------------------------------------------
    # Update Conversation Context
    # --------------------------------------------------

    def update_context(self, **kwargs):

        print(self.context.keys())

        for key, value in kwargs.items():

            if key not in self.context:

                raise KeyError(
                    f"'{key}' is not a valid context field."
                )

            self.context[key] = value

    # --------------------------------------------------
    # Get Conversation Context
    # --------------------------------------------------

    def get_context(self):

        return self.context

    # --------------------------------------------------
    # Clear Conversation Context
    # --------------------------------------------------

    def clear_context(self):

        self.context = self._default_context()

    # --------------------------------------------------
    # Reset Conversation
    # --------------------------------------------------

    def reset(self):

        self.clear_history()

        self.clear_context()

    # --------------------------------------------------
    # Update Context From Data Understanding Result
    # --------------------------------------------------

    def update_from_result(self, result):

        if result is None:
            raise ValueError(
                "Data understanding result cannot be None."
            )

        self.update_context(

            selected_dataset=result.selected_dataset,

            dataset_confidence=result.dataset_confidence,

            metrics=list(result.metrics),

            dimensions=list(result.dimensions),

            filters=list(result.filters)
        )

    # --------------------------------------------------
    # Check Whether Conversation Has Context
    # --------------------------------------------------

    def has_context(self):

        return bool(
            self.context.get("selected_dataset")
            or self.context.get("metrics")
            or self.context.get("dimensions")
            or self.context.get("filters")
        )
