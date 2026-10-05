"""
============================================================
MedIntel360
Insight Generator

Converts validated database results into a concise
natural-language analytical response.

The InsightGenerator does NOT execute SQL and does NOT
access the database directly.

Author : Jainam Gada
============================================================
"""

from dataclasses import dataclass
from typing import Any
from ai_engine.response_formatter import ResponseFormatter

# ============================================================
# INSIGHT GENERATION RESULT
# ============================================================

@dataclass
class InsightGenerationResult:

    answer: str

    has_data: bool

    truncated: bool = False

    error: str | None = None


# ============================================================
# INSIGHT GENERATOR
# ============================================================

class InsightGenerator:

    def __init__(
        self,
        llm_client
    ):

        self.llm = llm_client

    # --------------------------------------------------------
    # PUBLIC METHOD
    # --------------------------------------------------------

    def generate(
        self,
        query: str,
        execution_result,
        understanding_result=None
    ) -> InsightGenerationResult:

        # ----------------------------------------------
        # Validate query
        # ----------------------------------------------

        if not isinstance(query, str):

            raise TypeError(
                "Query must be a string."
            )

        query = query.strip()

        if not query:

            raise ValueError(
                "Query cannot be empty."
            )

        # ----------------------------------------------
        # Handle execution failure
        # ----------------------------------------------

        if not execution_result.success:

            return InsightGenerationResult(

                answer="",

                has_data=False,

                truncated=False,

                error=execution_result.error
            )

        # ----------------------------------------------
        # Handle empty result
        # ----------------------------------------------

        if execution_result.row_count == 0:

            return InsightGenerationResult(

                answer=(
                    "No data was found for this query."
                ),

                has_data=False,

                truncated=False,

                error=None
            )

        # ----------------------------------------------
        # Build AI context
        # ----------------------------------------------

        context = self._build_result_context(
            execution_result
        )

        # ----------------------------------------------
        # Build prompts
        # ----------------------------------------------

        system_prompt = self._build_system_prompt()

        user_prompt = self._build_user_prompt(
            query=query,
            context=context,
            understanding_result=understanding_result
        )

        # ----------------------------------------------
        # Call LLM
        # ----------------------------------------------

        try:

            response = self.llm.chat(

                system_prompt=system_prompt,

                user_prompt=user_prompt,

                temperature=0.1,

                max_tokens=1000
            )

        except Exception as error:

            return InsightGenerationResult(

                answer="",

                has_data=True,

                truncated=execution_result.truncated,

                error=str(error)
            )

        # ----------------------------------------------
        # Validate response
        # ----------------------------------------------

        if response is None:

            return InsightGenerationResult(

                answer="",

                has_data=True,

                truncated=execution_result.truncated,

                error=(
                    "Insight generation returned "
                    "no response."
                )
            )

        answer = ResponseFormatter.format(response)

        if not answer:

            return InsightGenerationResult(

                answer="",

                has_data=True,

                truncated=execution_result.truncated,

                error=(
                    "Insight generation returned "
                    "an empty response."
                )
            )

        # ----------------------------------------------
        # Return result
        # ----------------------------------------------

        return InsightGenerationResult(

            answer=answer,

            has_data=True,

            truncated=execution_result.truncated,

            error=None
        )

    # --------------------------------------------------------
    # RESULT CONTEXT
    # --------------------------------------------------------

    def _build_result_context(
        self,
        execution_result
    ) -> dict[str, Any]:

        return {

            "columns": list(
                execution_result.columns
            ),

            "rows": list(
                execution_result.rows
            ),

            "row_count": execution_result.row_count,

            "truncated": execution_result.truncated
        }

    # --------------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------------

    def _build_system_prompt(self):

        return """
You are the analytical response component of MedIntel360.

Your job is to answer the user's analytical question
using ONLY the database result supplied to you.

Rules:

1. Do not invent facts.

2. Do not invent values that are not present
   in the supplied result.

3. Do not claim that you accessed the database.

4. Do not execute SQL.

5. Do not provide SQL unless the user explicitly
   asks for the generated SQL.

6. Base numerical statements only on the supplied
   database result.

7. If the result contains multiple rows, summarize
   the most relevant findings clearly.

8. If the result was truncated, do not imply that
   the displayed rows represent the complete result.

9. Keep the answer concise and directly related
   to the user's question.

10. If the available result is insufficient to
    confidently answer the question, say so.

Return only the natural-language analytical answer.
"""

    # --------------------------------------------------------
    # USER PROMPT
    # --------------------------------------------------------

    def _build_user_prompt(
        self,
        query: str,
        context: dict[str, Any],
        understanding_result=None
    ):

        analytical_context = ""

        if understanding_result is not None:

            analytical_context = f"""
Structured analytical context:

Dataset:
{understanding_result.selected_dataset}

Metrics:
{understanding_result.metrics}

Dimensions:
{understanding_result.dimensions}

Filters:
{understanding_result.filters}
"""

        return f"""
USER QUESTION:

{query}

{analytical_context}

DATABASE RESULT:

Columns:
{context["columns"]}

Rows:
{context["rows"]}

Row Count:
{context["row_count"]}

Result Truncated:
{context["truncated"]}

Using only the supplied database result, answer
the user's question.
"""