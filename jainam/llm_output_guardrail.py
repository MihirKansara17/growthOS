"""
============================================================
MedIntel360
LLM Output Guardrail

Validates structured output returned by the LLM before
the result is allowed to continue into SQL generation.

The LLM is treated as an untrusted interpreter.

Author : Jainam Gada
============================================================
"""


class LLMOutputGuardrail:

    # ========================================================
    # Main Validation
    # ========================================================

    def validate(
        self,
        data,
        schema_manager
    ):
        """
        Validate structured LLM output against the
        MedIntel360 schema.

        Returns:
            {
                "valid": True/False,
                "data": original_data,
                "errors": []
            }
        """

        errors = []

        # ----------------------------------------------------
        # Basic structure
        # ----------------------------------------------------

        if not isinstance(data, dict):

            errors.append(
                "LLM output must be a JSON object."
            )

            return self._result(
                False,
                data,
                errors
            )

        # ----------------------------------------------------
        # Required top-level fields
        # ----------------------------------------------------

        required_fields = (
            "selected_dataset",
            "metrics",
            "dimensions",
            "filters",
        )

        for field in required_fields:

            if field not in data:

                errors.append(
                    f"Missing required field: {field}"
                )

        if errors:

            return self._result(
                False,
                data,
                errors
            )

        dataset = data.get(
            "selected_dataset"
        )

        metrics = data.get(
            "metrics"
        )

        dimensions = data.get(
            "dimensions"
        )

        filters = data.get(
            "filters"
        )

        # ----------------------------------------------------
        # Dataset validation
        # ----------------------------------------------------

        valid_datasets = set(
            schema_manager.get_dataset_names()
        )

        if not isinstance(
            dataset,
            str
        ):

            errors.append(
                "selected_dataset must be a string."
            )

        elif dataset not in valid_datasets:

            errors.append(
                f"Invalid dataset: {dataset}"
            )

        # ----------------------------------------------------
        # Metrics structure
        # ----------------------------------------------------

        if not isinstance(
            metrics,
            list
        ):

            errors.append(
                "metrics must be a list."
            )

        # ----------------------------------------------------
        # Dimensions structure
        # ----------------------------------------------------

        if not isinstance(
            dimensions,
            list
        ):

            errors.append(
                "dimensions must be a list."
            )

        # ----------------------------------------------------
        # Filters structure
        # ----------------------------------------------------

        if not isinstance(
            filters,
            list
        ):

            errors.append(
                "filters must be a list."
            )

        # ----------------------------------------------------
        # Stop if basic structures are invalid
        # ----------------------------------------------------

        if errors:

            return self._result(
                False,
                data,
                errors
            )

        # ----------------------------------------------------
        # Get valid schema metadata
        # ----------------------------------------------------

        valid_metrics = {
            metric["name"]
            for metric in schema_manager.get_metrics(
                dataset
            )
        }

        valid_dimensions = {
            dimension["name"]
            for dimension in schema_manager.get_dimensions(
                dataset
            )
        }

        # ----------------------------------------------------
        # Metric validation
        # ----------------------------------------------------

        for metric in metrics:

            if not isinstance(
                metric,
                str
            ):

                errors.append(
                    "Every metric must be a string."
                )

                continue

            if metric not in valid_metrics:

                errors.append(
                    f"Invalid metric: {metric}"
                )

        # ----------------------------------------------------
        # Dimension validation
        # ----------------------------------------------------

        for dimension in dimensions:

            if not isinstance(
                dimension,
                str
            ):

                errors.append(
                    "Every dimension must be a string."
                )

                continue

            if dimension not in valid_dimensions:

                errors.append(
                    f"Invalid dimension: {dimension}"
                )

        # ----------------------------------------------------
        # Filter validation
        # ----------------------------------------------------

        for index, filter_item in enumerate(
            filters
        ):

            self._validate_filter(
                filter_item,
                index,
                valid_dimensions,
                errors
            )

        # ----------------------------------------------------
        # Confidence validation
        # ----------------------------------------------------

        confidence = data.get(
            "dataset_confidence",
            0.0
        )

        if not isinstance(
            confidence,
            (int, float)
        ):

            errors.append(
                "dataset_confidence must be numeric."
            )

        elif not 0.0 <= confidence <= 1.0:

            errors.append(
                "dataset_confidence must be between 0 and 1."
            )

        # ----------------------------------------------------
        # Clarification validation
        # ----------------------------------------------------

        requires_clarification = data.get(
            "requires_clarification",
            False
        )

        if not isinstance(
            requires_clarification,
            bool
        ):

            errors.append(
                "requires_clarification must be boolean."
            )

        # ----------------------------------------------------
        # Clarification consistency
        # ----------------------------------------------------

        clarification_question = data.get(
            "clarification_question"
        )

        if (
            requires_clarification
            and not clarification_question
        ):

            errors.append(
                "clarification_question is required "
                "when requires_clarification is true."
            )

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        return self._result(
            len(errors) == 0,
            data,
            errors
        )

    # ========================================================
    # Filter Validation
    # ========================================================

    @staticmethod
    def _validate_filter(
        filter_item,
        index,
        valid_dimensions,
        errors
    ):

        if not isinstance(
            filter_item,
            dict
        ):

            errors.append(
                f"Filter {index} must be an object."
            )

            return

        # ----------------------------------------------------
        # Required filter fields
        # ----------------------------------------------------

        column = filter_item.get(
            "column"
        )

        operator = filter_item.get(
            "operator"
        )

        if not column:

            errors.append(
                f"Filter {index} is missing column."
            )

            return

        if not operator:

            errors.append(
                f"Filter {index} is missing operator."
            )

            return

        # ----------------------------------------------------
        # Column validation
        # ----------------------------------------------------

        if column not in valid_dimensions:

            errors.append(
                f"Invalid filter column: {column}"
            )

        # ----------------------------------------------------
        # Operator validation
        # ----------------------------------------------------

        allowed_operators = {
            "=",
            "!=",
            ">",
            "<",
            ">=",
            "<=",
            "in",
            "not in",
            "contains",
        }

        if operator.lower() not in allowed_operators:

            errors.append(
                f"Invalid filter operator: {operator}"
            )

        # ----------------------------------------------------
        # Value validation
        # ----------------------------------------------------

        if "value" not in filter_item:

            errors.append(
                f"Filter {index} is missing value."
            )

    # ========================================================
    # Result Helper
    # ========================================================

    @staticmethod
    def _result(
        valid,
        data,
        errors
    ):

        return {
            "valid": valid,
            "data": data,
            "errors": errors
        }