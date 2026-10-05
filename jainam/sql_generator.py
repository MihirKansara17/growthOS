from dataclasses import dataclass
from typing import List
from unittest import result


@dataclass
class SQLGenerationResult:

    sql: str

    dataset: str

    metrics: List[str]

    dimensions: List[str]

    filters: List[str]


class SQLGenerator:

    def __init__(self, schema_manager):

        self.schema = schema_manager


    # ==================================================
    # METRIC RESOLUTION
    # ==================================================

    def _resolve_metric(
        self,
        dataset,
        metric_name
    ):

        metrics = self.schema.get_metrics(
            dataset
        )

        for metric in metrics:

            if metric["name"] == metric_name:

                return metric

        raise ValueError(
            f"Metric '{metric_name}' does not exist "
            f"in dataset '{dataset}'."
        )


    # ==================================================
    # DIMENSION RESOLUTION
    # ==================================================

    def _resolve_dimension(
        self,
        dataset,
        dimension_name
    ):

        dimensions = self.schema.get_dimensions(
            dataset
        )

        for dimension in dimensions:

            if dimension["name"] == dimension_name:

                return dimension

        raise ValueError(
            f"Dimension '{dimension_name}' does not exist "
            f"in dataset '{dataset}'."
        )


    # ==================================================
    # GENERATE SQL
    # ==================================================

    def generate(
        self,
        understanding_result
    ):

        dataset = (
            understanding_result.selected_dataset
        )

        metrics = (
            understanding_result.metrics
        )

        dimensions = (
            understanding_result.dimensions
        )

        filters = (
            understanding_result.filters
        )


        # ----------------------------------------------
        # Basic validation
        # ----------------------------------------------

        if not dataset:

            raise ValueError(
                "Cannot generate SQL without a dataset."
            )


        if not metrics:

            raise ValueError(
                "Cannot generate SQL without metrics."
            )

        # ----------------------------------------------
        # Resolve physical database table
        # ----------------------------------------------

        dataset_definition = self.schema.get_dataset(
            dataset
        )

        if not dataset_definition:

            raise ValueError(
                f"Unknown dataset '{dataset}'."
            )

        physical_table = (
            dataset_definition["dataset_info"]["table"]
        )
        # ----------------------------------------------
        # SELECT expressions
        # ----------------------------------------------

        select_parts = []


        # ----------------------------------------------
        # Dimensions
        # ----------------------------------------------

        for dimension_name in dimensions:

            dimension = self._resolve_dimension(
                dataset,
                dimension_name
            )

            select_parts.append(
                dimension["name"]
            )


        # ----------------------------------------------
        # Metrics
        # ----------------------------------------------

        for metric_name in metrics:

            metric = self._resolve_metric(
                dataset,
                metric_name
            )

            aggregation = metric.get(
                "default_aggregation"
            )

            if not aggregation:

                raise ValueError(
                    f"Metric '{metric_name}' has no "
                    f"default aggregation."
                )


            expression = (
                f"{aggregation}({metric['name']}) "
                f"AS {metric['name']}"
            )

            select_parts.append(
                expression
            )


        # ----------------------------------------------
        # SELECT
        # ----------------------------------------------

        select_clause = ", ".join(
            select_parts
        )


        sql = (
            f"SELECT {select_clause} "
            f"FROM {physical_table}"
        )

        # ----------------------------------------------
        # WHERE
        # ----------------------------------------------

        resolved_filters = []

        if understanding_result.filters:

            for filter_definition in understanding_result.filters:

                resolved_filter = self._resolve_filter(
                    dataset,
                    filter_definition
                )

                resolved_filters.append(
                    self._filter_to_sql(
                    resolved_filter
                )
                )


        where_clause = " AND ".join(
            resolved_filters
        )

        if where_clause:

            sql += f" WHERE {where_clause}"

        # ----------------------------------------------
        # GROUP BY
        # ----------------------------------------------

        if dimensions:

            group_by = ", ".join(
                dimensions
            )

            sql += (
                f" GROUP BY {group_by}"
            )


        return SQLGenerationResult(

            sql=sql,

            dataset=dataset,

            metrics=metrics,

            dimensions=dimensions,

            filters=filters
        )

    def _resolve_filter(
        self,
        dataset,
        filter_definition
    ):

        if not isinstance(filter_definition, dict):

            raise ValueError(
                "Filter must be a dictionary."
            )


        dimension_name = filter_definition.get(
            "dimension"
        )

        operator = filter_definition.get(
            "operator"
        )

        value = filter_definition.get(
            "value"
        )


        if not dimension_name:

            raise ValueError(
                "Filter is missing 'dimension'."
            )


        if not operator:

            raise ValueError(
                "Filter is missing 'operator'."
            )


        if "value" not in filter_definition:

            raise ValueError(
                "Filter is missing 'value'."
            )


        # ----------------------------------------------
        # Validate dimension against schema
        # ----------------------------------------------

        dimension = self._resolve_dimension(
            dataset,
            dimension_name
        )


        # ----------------------------------------------
        # Supported operators
        # ----------------------------------------------

        allowed_operators = {
            "=",
            "!=",
            ">",
            "<",
            ">=",
            "<=",
            "LIKE",
            "IN"
        }


        if operator.upper() not in allowed_operators:

            raise ValueError(
                f"Unsupported filter operator: "
                f"'{operator}'."
            )


        return {
            "dimension": dimension["name"],
            "operator": operator.upper(),
            "value": value
        }

    def _filter_to_sql(
        self,
        filter_definition
    ):

        dimension = filter_definition[
            "dimension"
        ]

        operator = filter_definition[
            "operator"
        ]

        value = filter_definition[
            "value"
        ]


        # ----------------------------------------------
        # IN
        # ----------------------------------------------

        if operator == "IN":

            if not isinstance(value, list):

                raise ValueError(
                    "IN filter requires a list of values."
                )

            values = ", ".join(
                self._quote_value(item)
                for item in value
            )

            return (
                f"{dimension} IN ({values})"
            )


        # ----------------------------------------------
        # Normal operators
        # ----------------------------------------------

        return (
            f"{dimension} "
            f"{operator} "
            f"{self._quote_value(value)}"
        )

    def _quote_value(
        self,
        value
    ):

        if value is None:

            return "NULL"


        if isinstance(value, bool):

            return (
                "TRUE"
                if value
                else "FALSE"
            
            )


        if isinstance(value, (int, float)):

            return str(value)


        if isinstance(value, str):

            escaped = value.replace(
                "'",
                "''"
            )

            return f"'{escaped}'"


        raise ValueError(
            f"Unsupported filter value type: "
            f"{type(value).__name__}"
        )