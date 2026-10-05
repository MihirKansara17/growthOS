"""
============================================================
MedIntel360
Query Engine

End-to-end natural-language analytics orchestration.

Flow:
User Query
    ↓
Data Understanding
    ↓
SQL Generation
    ↓
SQL Validation
    ↓
Database Execution
    ↓
Insight Generation
    ↓
Response Formatting

Author : Jainam Gada
============================================================
"""
from dataclasses import dataclass
from ai_engine.data_understanding_agent import DataUnderstandingAgent
from ai_engine.sql_generator import SQLGenerator
from ai_engine.sql_validator import SQLValidator
from ai_engine.insight_generator import InsightGenerator
from ai_engine.schema_manager import SchemaManager
from ai_engine.conversation_manager import ConversationManager
from database.executor import DatabaseExecutor

# ============================================================
# QUERY ENGINE RESULT
# ============================================================

@dataclass
class QueryEngineResult:

    answer: str

    success: bool

    sql: str = ""

    error: str | None = None

    truncated: bool = False


# ============================================================
# QUERY ENGINE
# ============================================================

class QueryEngine:

    def __init__(
        self,
        llm_client,
        max_rows: int = 1000
    ):

        self.llm = llm_client

        # Shared semantic schema
        self.schema_manager = SchemaManager()

        # Conversation state
        self.conversation_manager = ConversationManager()

        # Agents / pipeline components
        self.understanding_agent = DataUnderstandingAgent(
            self.schema_manager,
            self.conversation_manager,
            self.llm
        )

        self.sql_generator = SQLGenerator(
            self.schema_manager
        )

        self.sql_validator = SQLValidator(
            self.schema_manager
        )

        self.executor = DatabaseExecutor(
            max_rows=max_rows
        )

        self.insight_generator = InsightGenerator(
            self.llm
            )

    # ========================================================
    # PUBLIC QUERY METHOD
    # ========================================================
    def ask(self, query: str) -> QueryEngineResult:

        if not isinstance(query, str):
            raise TypeError("Query must be a string.")

        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        # ----------------------------------------------------
        # 1. Data Understanding
        # ----------------------------------------------------

        try:

            understanding_result = self.understanding_agent.understand(query)

            if understanding_result.requires_clarification:

                return QueryEngineResult(
                    answer=understanding_result.clarification_question or
                    "Please clarify your question.",
                    success=True
                    )

        except Exception as error:

            return QueryEngineResult(
                answer="",
                success=False,
                error=str(error)
            )

        # ----------------------------------------------------
        # 2. SQL Generation
        # ----------------------------------------------------

        try:

            sql_result = self.sql_generator.generate(
                            understanding_result
                        )
        except Exception as error:

            return QueryEngineResult(
                answer="",
                success=False,
                error=str(error)
            )

        # ----------------------------------------------------
        # Extract SQL
        # ----------------------------------------------------

        sql = (
            sql_result.sql
            if hasattr(sql_result, "sql")
            else str(sql_result)
        )

        if not sql or not sql.strip():

            return QueryEngineResult(
                answer="",
                success=False,
                error="SQL generation returned an empty query."
            )

        # ----------------------------------------------------
        # 3. SQL Validation
        # ----------------------------------------------------

        try:

            validation_result = (
                self.sql_validator.validate(sql)
            )

        except Exception as error:

            return QueryEngineResult(
                answer="",
                success=False,
                sql=sql,
                error=str(error)
            )

        if not validation_result.valid:

            return QueryEngineResult(
                answer="",
                success=False,
                sql=sql,
                error="; ".join(validation_result.errors)
            )

        # ----------------------------------------------------
        # 4. Database Execution
        # ----------------------------------------------------

        execution_result = self.executor.execute(sql)

        if not execution_result.success:

            return QueryEngineResult(
                answer="",
                success=False,
                sql=sql,
                error=execution_result.error
            )

        # ----------------------------------------------------
        # 5. Insight Generation
        # ----------------------------------------------------

        insight_result = (
            self.insight_generator.generate(
                query=query,
                execution_result=execution_result,
                understanding_result=understanding_result
            )
        )

        if insight_result.error:

            return QueryEngineResult(
                answer="",
                success=False,
                sql=sql,
                truncated=execution_result.truncated,
                error=insight_result.error
            )

        # ----------------------------------------------------
        # 6. Final Response
        # ----------------------------------------------------

        return QueryEngineResult(

            answer=insight_result.answer,

            success=True,

            sql=sql,

            truncated=execution_result.truncated,

            error=None
        )