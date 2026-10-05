import json
from dataclasses import dataclass, field
from typing import Any
from ai_engine.input_guardrail import InputGuardrail
from ai_engine.base_agent import BaseAgent
from ai_engine.llm_output_guardrail import LLMOutputGuardrail

# ============================================================
# Data Understanding Result
# ============================================================

@dataclass
class DataUnderstandingResult:

    query: str

    intent: str | None = None

    selected_dataset: str | None = None

    dataset_confidence: float = 0.0

    metrics: list[str] = field(
        default_factory=list
    )

    dimensions: list[str] = field(
        default_factory=list
    )

    filters: list[dict[str, Any]] = field(
        default_factory=list
    )

    group_by: list[str] = field(
        default_factory=list
    )

    sort_by: dict[str, Any] | None = None

    limit: int | None = None
    
    requires_clarification: bool = False

    clarification_question: str | None = None


# ============================================================
# Data Understanding Agent
# ============================================================

class DataUnderstandingAgent(BaseAgent):

    def __init__(
        self,
        schema_manager,
        conversation_manager,
        llm_client
    ):

        super().__init__()

        self.schema = schema_manager

        self.conversation = conversation_manager

        self.llm = llm_client
        self.input_guardrail = InputGuardrail()
        self.llm_output_guardrail = LLMOutputGuardrail()
    # --------------------------------------------------------
    # BaseAgent Requirement
    # --------------------------------------------------------

    def get_summary(self):

        return {
            "agent": "DataUnderstandingAgent",
            "status": "initialized"
        }

    # --------------------------------------------------------
    # BaseAgent Requirement
    # --------------------------------------------------------

    def answer(self, query):

        return self.understand(query)

     # --------------------------------------------------------
    # Main Public Method
    # --------------------------------------------------------

    def understand(
        self,
        query: str
    ) -> DataUnderstandingResult:

        # --------------------------------------------------
        # Validate Query
        # --------------------------------------------------

        if not isinstance(query, str):

            raise TypeError(
                "Query must be a string."
            )

        query = query.strip()

        if not query:

            raise ValueError(
                "Query cannot be empty."
            )

        # --------------------------------------------------
        # Preprocess
        # --------------------------------------------------

        query = self._preprocess_query(
            query
        )

        # --------------------------------------------------
        # Input Guardrail
        # --------------------------------------------------

        guardrail_result = self.input_guardrail.validate(
            query
        )

        if not guardrail_result["allowed"]:

            return DataUnderstandingResult(

                query=query,

                requires_clarification=True,

                clarification_question=(
                    "I can't process that request. "
                    "Please provide a valid analytical "
                    "question about the available data."
                )
            )

        query = guardrail_result["query"]
        # --------------------------------------------------
        # Retrieve Previous Context
        # --------------------------------------------------

        conversation_context = (
            self.conversation.get_context()
        )

        # --------------------------------------------------
        # Detect Follow-Up
        # --------------------------------------------------

        is_follow_up = self.is_follow_up(
            query=query,
            conversation_context=conversation_context
        )

        print()
        print("=" * 60)
        print("FOLLOW-UP DETECTION")
        print("=" * 60)

        print()
        print("Query:")
        print(query)

        print()
        print("Detected Follow-Up:")
        print(is_follow_up)

        print("=" * 60)

        # --------------------------------------------------
        # Store User Message
        # --------------------------------------------------

        self.conversation.add_message(
            "user",
            query
        )

        # --------------------------------------------------
        # Retrieve Schema Metadata
        # --------------------------------------------------

        metadata = self._search_metadata(
            query
        )

        # --------------------------------------------------
        # Debug Output
        # --------------------------------------------------

        print()
        print("=" * 60)
        print("SCHEMA METADATA RETRIEVAL")
        print("=" * 60)

        print()
        print("Query:")
        print(query)

        print()
        print("Datasets:")
        print(metadata["datasets"])

        print()
        print("Metrics:")
        print(metadata["metrics"])

        print()
        print("Dimensions:")
        print(metadata["dimensions"])

        print()
        print("Glossary:")
        print(metadata["glossary"])

        print("=" * 60)

        # --------------------------------------------------
        # No Candidates
        #
        # Only reject if this is NOT a follow-up.
        # --------------------------------------------------

        if not metadata["datasets"] and not is_follow_up:

            return DataUnderstandingResult(

                query=query,

                requires_clarification=True,

                clarification_question=(
                    "I could not identify the relevant "
                    "dataset. Could you clarify what "
                    "you want to analyze?"
                )
            )

        # --------------------------------------------------
        # LLM Interpretation
        # --------------------------------------------------

        result = self._get_llm_result(
            query=query,
            metadata=metadata,
            conversation_context=conversation_context
        )

        # --------------------------------------------------
        # Update Conversation Context
        # --------------------------------------------------

        self.conversation.update_context(
            selected_dataset=result.selected_dataset,
            dataset_confidence=result.dataset_confidence,
            metrics=result.metrics,
            dimensions=result.dimensions,
            filters=result.filters
        )

        self.conversation.update_from_result(
            result
        )

        # --------------------------------------------------
        # Store Assistant Response
        # --------------------------------------------------

        self.conversation.add_message(
            "assistant",
            str(result)
        )

        # --------------------------------------------------
        # Debug Output
        # --------------------------------------------------

        print()
        print("=" * 60)
        print("FINAL DATA UNDERSTANDING RESULT")
        print("=" * 60)

        print(result)

        print("=" * 60)

        return result

    # --------------------------------------------------------
    # Query Preprocessing
    # --------------------------------------------------------

    @staticmethod
    def _preprocess_query(query: str) -> str:

        if not isinstance(query, str):

            raise TypeError(
                "Query must be a string."
            )

        query = query.strip()

        if not query:

            raise ValueError(
                "Query cannot be empty."
            )

        # Collapse multiple spaces into one
        query = " ".join(query.split())

        return query
    # --------------------------------------------------------
    # Schema Metadata Retrieval
    # --------------------------------------------------------

    def _search_metadata(self, query):

        ranked_datasets = (
            self.schema.rank_dataset_candidates(
                query
            )
        )

        candidates = []

        for candidate in ranked_datasets:

            dataset_name = candidate[
                "dataset"
            ]

            metrics = self.schema.search_metrics(
                dataset_name,
                query
            )

            dimensions = self.schema.search_dimensions(
                dataset_name,
                query
            )

            candidates.append({

                "dataset": dataset_name,

                "ranking": candidate,

                "metrics": metrics,

                "dimensions": dimensions

            })

        # --------------------------------------------------
        # Best candidate
        # --------------------------------------------------

        if candidates:

            best = candidates[0]

            metrics = best["metrics"]

            dimensions = best["dimensions"]

        else:

            metrics = []

            dimensions = []

        return {

            "datasets": ranked_datasets,

            "metrics": metrics,

            "dimensions": dimensions,

            "glossary": self.schema.search_glossary(
                query
            ),

            "candidates": candidates
        }

    def _get_ranked_datasets(self, query):

        return self.schema.rank_dataset_candidates(
            query
        )

    def _get_candidate_metadata(
        self,
        query,
        ranked_datasets
    ):

        metadata = []

        for candidate in ranked_datasets:

            dataset_name = candidate[
            "dataset"
            ]

            metrics = self.schema.search_metrics(
                dataset_name,
                query
            )

            dimensions = self.schema.search_dimensions(
                dataset_name,
                query
            )

            metadata.append({

                "dataset": dataset_name,

                "ranking": candidate,

                "metrics": metrics,

                "dimensions": dimensions

            })

        return metadata

    def _build_initial_result(
        self,
        query,
        metadata
    ):

        datasets = metadata["datasets"]

        # --------------------------------------------------
        # No dataset found
        # --------------------------------------------------

        if not datasets:

            return DataUnderstandingResult(

                query=query,

                requires_clarification=True,

                clarification_question=(
                    "I could not identify the "
                    "relevant dataset. Could you "
                    "clarify what you want to analyze?"
                )
            )

        # --------------------------------------------------
        # Select highest-ranked dataset
        # --------------------------------------------------

        best_dataset = datasets[0]

        selected_dataset = best_dataset[
            "dataset"
        ]

        total_score = best_dataset[
            "total_score"
        ]

        # --------------------------------------------------
        # Calculate confidence
        # --------------------------------------------------

        if len(datasets) > 1:

            second_score = datasets[1][
                "total_score"
            ]

        else:

            second_score = 0

        if total_score == 0:

            confidence = 0.0

        elif second_score == 0:

            confidence = 1.0

        else:

            confidence = (
                total_score
                /
                (
                    total_score
                    + second_score
                )
            )

        # --------------------------------------------------
        # Best candidate metadata
        # --------------------------------------------------

        candidates = metadata[
            "candidates"
        ]

        best_candidate = candidates[0]

        metrics = self._select_metrics(
            best_candidate["metrics"]
        )

        dimensions = self._select_dimensions(
            best_candidate["dimensions"]
        )

        # --------------------------------------------------
        # Build result
        # --------------------------------------------------

        return DataUnderstandingResult(

            query=query,

            selected_dataset=selected_dataset,

            dataset_confidence=round(
                confidence,
                3
            ),

            metrics=metrics,

            dimensions=dimensions
        )

    def _select_metrics(self, metrics):

        if not metrics:
            return []

        # Metrics are already sorted by:
        # search score → search weight

        return [
            metrics[0]["name"]
        ]

    def _select_dimensions(self, dimensions):

        if not dimensions:
            return []

        return [
            dimensions[0]["name"]
        ]

    def _build_llm_prompt(
    self,
    query,
    metadata,
    conversation_context=None
    ):

        return f"""
    You are the query understanding component
        of MedIntel360.

    Your task is to interpret the user's analytical
        query using ONLY the schema information provided
        and, when applicable, the previous analytical
        context.

    CURRENT USER QUERY:
    {query}

    PREVIOUS ANALYTICAL CONTEXT:
    {conversation_context}

    AVAILABLE DATASETS:
    {metadata["datasets"]}

    AVAILABLE METRICS:
    {metadata["metrics"]}

    AVAILABLE DIMENSIONS:
    {metadata["dimensions"]}

    GLOSSARY:
    {metadata["glossary"]}

    RULES:

    1. Select the dataset that best matches the query.

    2. Select only the metrics required to answer
        the query.

    3. Select only the dimensions required by the query.

    4. Do not invent dataset names, metric names,
        dimension names, or column names.

    5. If the query asks for grouping such as
        "by department", select the corresponding
        dimension.

    6. Respect the default aggregation associated
        with the selected metric.

    7. If the current query is a follow-up to the
        previous analytical context, preserve the
        relevant dataset, metrics, and dimensions
        from that context.

    8. A follow-up query may add or modify filters.

    9. If the user says something like
        "Only Cardiology", "Just Neurology", or
        "For Cardiology", interpret it as a filter
        on the relevant dimension from the previous
        analytical context.

    10. Do not require the user to repeat information
        that already exists in the previous context.

    11. Only introduce a filter when it is supported
        by the available schema.

    12. If the query is genuinely ambiguous and cannot
        be resolved using the current query, schema,
        and previous context, indicate that
        clarification is required.

        Return ONLY valid JSON in this format:

        {{
            "intent": "string",
            "selected_dataset": "string or null",
            "dataset_confidence": 0.0,
            "metrics": [],
            "dimensions": [],
            "filters": [],
            "requires_clarification": false,
            "clarification_question": null
        }}
    """
    def _call_llm(
        self,
        query,
        metadata,
        conversation_context=None
    ):

        # --------------------------------------------------
        # Conversation Context
        # --------------------------------------------------

        if conversation_context:

            context_text = f"""
                Previous analytical context:

                Dataset:
                    {conversation_context.get("selected_dataset")}

                Dataset Confidence:
                    {conversation_context.get("dataset_confidence")}

                Metrics:
                    {conversation_context.get("metrics")}

                Dimensions:
                    {conversation_context.get("dimensions")}

                Filters:
                    {conversation_context.get("filters")}

                Group By:
                    {conversation_context.get("group_by")}

                Sort By:
                {conversation_context.get("sort_by")}

                Limit:
                    {conversation_context.get("limit")}
                """

        else:

            context_text = """
                No previous analytical context exists.
            """

        # --------------------------------------------------
        # System Prompt
        # --------------------------------------------------

        system_prompt = """
            You are a structured query understanding
            assistant for MedIntel360.

            Your job is to understand the user's
            current analytical request.

            You will receive:

            1. Current user query
            2. Schema metadata
            3. Previous analytical context

            Rules:

            - Always follow the provided schema.
            - Never invent datasets.
            - Never invent metrics.
            - Never invent dimensions.
            - Never invent filters.
            - Use previous context when the current
                query is a follow-up.
            - A follow-up may modify, filter, extend,
                compare, sort, or limit the previous query.
            - Preserve relevant previous context when
                  interpreting follow-up queries.
            - Return valid JSON only.
            """

        # --------------------------------------------------
        # Build Prompt
        # --------------------------------------------------

        user_prompt = self._build_llm_prompt(
            query=query,
            metadata=metadata,
            conversation_context=context_text
        )

        # --------------------------------------------------
        # LLM Call
        # --------------------------------------------------

        response = self.llm.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0,
            max_tokens=800
        )

        return response

    def _normalize_llm_result(
        self,
        query,
        data
    ):

        metrics = []

        for metric in data.get(
            "metrics",
            []
        ):

            if isinstance(metric, dict):

                name = metric.get(
                    "name"
                )

                if name:
                    metrics.append(name)

            elif isinstance(metric, str):

                metrics.append(metric)

        dimensions = []

        for dimension in data.get(
            "dimensions",
            []
        ):

            if isinstance(dimension, dict):

                name = dimension.get(
                    "name"
                )

                if name:
                    dimensions.append(name)

            elif isinstance(dimension, str):

                dimensions.append(dimension)

        return DataUnderstandingResult(

            query=query,

            intent=data.get(
                "intent"
            ),

            selected_dataset=data.get(
                "selected_dataset"
            ),

            dataset_confidence=float(
                data.get(
                    "dataset_confidence",
                    0.0
                )
            ),

            metrics=metrics,

            dimensions=dimensions,

            filters=data.get(
                "filters",
                []
            ),

            requires_clarification=bool(
                data.get(
                    "requires_clarification",
                False
                )
            ),

            clarification_question=data.get(
                "clarification_question"
            )
        )

    def _validate_dataset(
        self,
        dataset_name
    ):

        if dataset_name is None:
            return False

        return dataset_name in (
            self.schema.get_dataset_names()
        )

    def _validate_metrics(
        self,
        dataset_name,
        metrics
    ):

        if not dataset_name:
            return False

        valid_metrics = {
            metric["name"]
            for metric in self.schema.get_metrics(
                dataset_name
            )
        }

        return all(
            metric in valid_metrics
            for metric in metrics
        )

    def _validate_dimensions(
        self,
        dataset_name,
        dimensions
    ):

        if not dataset_name:
            return False

        valid_dimensions = {
            dimension["name"]
            for dimension in self.schema.get_dimensions(
                dataset_name
            )
        }

        return all(
            dimension in valid_dimensions
            for dimension in dimensions
        )

    def _validate_llm_result(
        self,
        result
    ):

        dataset = result.selected_dataset

        # --------------------------------------------------
        # Dataset
        # --------------------------------------------------

        if not self._validate_dataset(
            dataset
        ):

            raise ValueError(
                f"Invalid dataset returned by LLM: "
                f"{dataset}"
            )

        # --------------------------------------------------
        # Metrics
        # --------------------------------------------------

        if not self._validate_metrics(
            dataset,
            result.metrics
        ):

            raise ValueError(
                "LLM returned one or more "
                "invalid metrics."
            )

        # --------------------------------------------------
        # Dimensions
        # --------------------------------------------------

        if not self._validate_dimensions(
            dataset,
            result.dimensions
        ):

            raise ValueError(
                "LLM returned one or more "
                "invalid dimensions."
            )

        return True

    def _get_llm_result(
        self,
        query,
        metadata,
        conversation_context=None
        ):

        # --------------------------------------------------
        # Call LLM
        # --------------------------------------------------

        response = self._call_llm(
            query=query,
            metadata=metadata,
            conversation_context=conversation_context
        )

        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------

        parsed = self._parse_llm_response(
            response
        )

        guardrail_result = self.llm_output_guardrail.validate( parsed,self.schema)

        if not guardrail_result["valid"]:

            raise ValueError(
                "LLM output failed guardrail validation: "
                +";".join(guardrail_result["errors"])
            )

        # --------------------------------------------------
        # Normalize
        # --------------------------------------------------

        result = self._normalize_llm_result(
            query,
            parsed
        )

        # --------------------------------------------------
        # Validate
        # --------------------------------------------------


        return result

    def is_follow_up(
        self,
        query: str,
        conversation_context=None
    ):

        if not self.conversation.has_context():

            return False

        query = query.strip().lower()

        follow_up_patterns = (

            "only ",
            "just ",
            "exclude ",
            "except ",
            "sort ",
            "order ",
            "limit ",
            "top ",
            "bottom ",
            "show more",
            "show less",
            "same",
            "those",
            "these"
        )

        return query.startswith(
            follow_up_patterns
        )

    def _get_conversation_context_for_llm(self):

        context = self.conversation.get_context()

        return {
            "selected_dataset": context.get(
                "selected_dataset"
            ),

            "metrics": context.get(
                "metrics",
                []
            ),

            "dimensions": context.get(
                "dimensions",
                []
            ),

            "filters": context.get(
                "filters",
                []
            ),

            "group_by": context.get(
                "group_by",
                []
            ),

            "sort_by": context.get(
                "sort_by"
            ),

            "limit": context.get(
                "limit"
            )
        }

    def _parse_llm_response(
        self,
        response
    ):
        """
        Parse the raw LLM response into a Python dictionary.
        """

        import json

        # --------------------------------------------------
        # Extract content from OpenRouter response
        # --------------------------------------------------

        if isinstance(response, dict):

            content = (
                response
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content")
            )

        else:
            content = response

        if not content:

            raise ValueError(
                "LLM response did not contain any content."
            )

        # --------------------------------------------------
        # Clean response
        # --------------------------------------------------

        content = content.strip()

        # Handle accidental markdown fences
        if content.startswith("```"):

            lines = content.splitlines()

            if lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------

        try:

            parsed = json.loads(content)

        except json.JSONDecodeError as exc:

            raise ValueError(
                f"LLM returned invalid JSON: {exc}"
            ) from exc

        # --------------------------------------------------
        # Validate basic structure
        # --------------------------------------------------

        if not isinstance(parsed, dict):

            raise ValueError(
                "LLM response must be a JSON object."
            )

        return parsed