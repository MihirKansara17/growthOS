from ai_engine.schema_manager import SchemaManager
from ai_engine.sql_generator import SQLGenerator

class SQLValidationResult:

    def __init__(
        self,
        valid,
        errors=None
    ):

        self.valid = valid
        self.errors = errors or []

    def __repr__(self):

        return (
            f"SQLValidationResult("
            f"valid={self.valid}, "
            f"errors={self.errors}"
            f")"
        )


class SQLValidator:

    def __init__(self, schema_manager):

        self.schema = schema_manager

    def validate(self, sql):

        errors = []

        # ----------------------------------------------
        # Basic validation
        # ----------------------------------------------

        if not isinstance(sql, str):

            errors.append(
                "SQL must be a string."
            )

            return SQLValidationResult(
                valid=False,
                errors=errors
            )

        sql = sql.strip()

        if not sql:

            errors.append(
                "SQL cannot be empty."
            )

            return SQLValidationResult(
                valid=False,
                errors=errors
            )

        # ----------------------------------------------
        # Only SELECT queries
        # ----------------------------------------------

        if not sql.upper().startswith("SELECT"):

            errors.append(
                "Only SELECT queries are allowed."
            )

        # ----------------------------------------------
        # Forbidden operations
        # ----------------------------------------------

        forbidden_keywords = [
            "DROP",
            "DELETE",
            "UPDATE",
            "INSERT",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "GRANT",
            "REVOKE"
        ]

        upper_sql = sql.upper()

        for keyword in forbidden_keywords:

            if keyword in upper_sql:

                errors.append(
                    f"Forbidden SQL operation: {keyword}"
                )

        # ----------------------------------------------
        # If basic validation failed,
        # don't attempt schema validation.
        # ----------------------------------------------

        if errors:

            return SQLValidationResult(
                valid=False,
                errors=errors
            )

        # ----------------------------------------------
        # Schema validation
        # ----------------------------------------------

        self._validate_schema(
            sql,
            errors
        )

        # ----------------------------------------------
        # Final result
        # ----------------------------------------------

        return SQLValidationResult(

            valid=len(errors) == 0,

            errors=errors
        )

    # ==================================================
    # Schema Validation
    # ==================================================
    def _validate_schema(
        self,
        sql,
        errors
    ):

        upper_sql = sql.upper()

        # ----------------------------------------------
        # Extract FROM value
        # ----------------------------------------------

        if " FROM " not in upper_sql:

            errors.append(
                "SQL query does not contain a FROM clause."
            )

            return

        from_index = upper_sql.index(" FROM ")

        after_from = sql[
            from_index + len(" FROM "):
        ].strip()

        dataset_reference = (
            after_from
            .split()[0]
            .strip()
        )

        dataset_reference = (
            dataset_reference.rstrip(";")
        )

        # ----------------------------------------------
        # Resolve logical dataset OR physical table
        # ----------------------------------------------

        logical_dataset = None

        # First: check whether it is already
        # a logical dataset ID.
        try:

            self.schema.get_dataset(
                dataset_reference
            )

            logical_dataset = dataset_reference

        except ValueError:

            # ------------------------------------------
            # Otherwise resolve physical table
            # ------------------------------------------

            for dataset_name, dataset_definition in (
                self.schema.datasets.items()
            ):

                dataset_info = dataset_definition.get(
                    "dataset_info",
                    {}
                )

                if (
                    dataset_info.get("table")
                    == dataset_reference
                ):

                    logical_dataset = dataset_name

                    break

        # ----------------------------------------------
        # Unknown dataset/table
        # ----------------------------------------------

        if logical_dataset is None:

            errors.append(
                f"Unknown dataset: {dataset_reference}"
            )

            return

        # ----------------------------------------------
        # Get schema metadata
        # ----------------------------------------------

        metrics = self.schema.get_metrics(
            logical_dataset
        )

        dimensions = self.schema.get_dimensions(
            logical_dataset
        )

        metric_names = {
            metric["name"]
            for metric in metrics
        }

        dimension_names = {
            dimension["name"]
            for dimension in dimensions
        }

        # ----------------------------------------------
        # Validate known SQL identifiers
        # ----------------------------------------------

        self._validate_identifiers(
            sql,
            metric_names,
            dimension_names,
            errors
        )

        self._validate_select_group_by(
            sql,
            metric_names,
            dimension_names,
            errors
        )

        self._validate_where(
            sql,
            dimension_names,
            metric_names,
            errors
        )

        self._validate_aggregations(
            sql,
            metric_names,
            dimension_names,
            errors
        )

        self._validate_select_expressions(
            sql,
            metric_names,
            dimension_names,
            errors
        )

        self._validate_where_operators(
            sql,
            errors
        )

        self._validate_having(
            sql,
            metric_names,
            dimension_names,
            errors
        )

        self._validate_order_by(
            sql,
            metric_names,
            dimension_names,
            errors
        )

        self._validate_limit(
            sql,
            errors
        )

        self._validate_security(
            sql,
            errors
        )
    # ==================================================
    # Identifier Validation
    # ==================================================

    def _validate_identifiers(
        self,
        sql,
        metric_names,
        dimension_names,
        errors
    ):

        # ----------------------------------------------
        # Extract identifiers appearing in SQL
        # ----------------------------------------------

        identifiers = set()

        for name in metric_names:

            if name.upper() in sql.upper():

                identifiers.add(name)

        for name in dimension_names:

            if name.upper() in sql.upper():

                identifiers.add(name)

        # ----------------------------------------------
        # Ensure SQL contains at least one
        # known schema field.
        # ----------------------------------------------

        if not identifiers:

            errors.append(
                "SQL does not reference any known "
                "metrics or dimensions."
            )

    # ==================================================
    # SELECT / GROUP BY Validation
    # ==================================================

    def _validate_select_group_by(
        self,
        sql,
        metric_names,
        dimension_names,
        errors
    ):
        import re
        upper_sql = sql.upper()

        # ----------------------------------------------
        # SELECT clause
        # ----------------------------------------------

        select_start = upper_sql.find("SELECT")
        from_start = upper_sql.find(" FROM ")

        if select_start == -1 or from_start == -1:

            errors.append(
                "Unable to determine SELECT clause."
            )

            return

        select_clause = sql[
            select_start + len("SELECT"):
            from_start
        ].strip()

        # ----------------------------------------------
        # GROUP BY clause
        # ----------------------------------------------

        group_by_start = upper_sql.find(
            " GROUP BY "
        )

        group_by_fields = []

        if group_by_start != -1:

            group_by_clause = sql[
                group_by_start + len(" GROUP BY "):
            ].strip()

            # Remove possible trailing clauses
            group_by_clause = sql[
                group_by_start + len(" GROUP BY "):
            ].strip()

        # Remove all possible trailing clauses
            group_by_clause = re.split(
                r"\bHAVING\b|\bORDER\s+BY\b|\bLIMIT\b",
                group_by_clause,
                maxsplit=1,
                flags=re.IGNORECASE
            )[0].rstrip(";").strip()

            group_by_fields = [
                field.strip()
                for field in group_by_clause.split(",")
            ]

        # ----------------------------------------------
        # Find selected dimensions
        # ----------------------------------------------

        selected_dimensions = []

        for dimension in dimension_names:

            if dimension.upper() in select_clause.upper():

                selected_dimensions.append(
                    dimension
                )

        # ----------------------------------------------
        # Every selected non-aggregated dimension
        # must appear in GROUP BY.
        # ----------------------------------------------

        for dimension in selected_dimensions:

            if dimension not in group_by_fields:

                errors.append(
                    f"Dimension '{dimension}' "
                    f"is selected but not present "
                    f"in GROUP BY."
                )

        # ----------------------------------------------
        # GROUP BY fields must be valid dimensions
        # ----------------------------------------------

        for field in group_by_fields:

            if field not in dimension_names:

                errors.append(
                    f"GROUP BY field '{field}' "
                    f"is not a valid dimension."
                )

    # ==================================================
    # WHERE / FILTER Validation
    # ==================================================

    def _validate_where(
        self,
        sql,
        dimension_names,
        metric_names,
        errors
    ):

        import re

        # ----------------------------------------------
        # Extract WHERE clause
        # ----------------------------------------------

        match = re.search(
            r"\bWHERE\b(.*?)(?:\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|$)",
            sql,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return

        where_clause = match.group(1).strip()

        if not where_clause:

            errors.append(
                "WHERE clause cannot be empty."
            )

            return

        # ----------------------------------------------
        # Split AND conditions
        # ----------------------------------------------

        conditions = re.split(
            r"\s+AND\s+",
            where_clause,
            flags=re.IGNORECASE
        )

        # ----------------------------------------------
        # Supported operators
        # ----------------------------------------------

        supported_operators = {
            "=",
            "!=",
            "<>",
            ">",
            "<",
            ">=",
            "<="
        }

        # ----------------------------------------------
        # Validate each condition
        # ----------------------------------------------

        for condition in conditions:

            condition = condition.strip()

            if not condition:

                errors.append(
                    "Empty WHERE condition."
                )

                continue

            # ------------------------------------------
            # Extract field / operator / value
            # ------------------------------------------

            operator_match = re.match(
                r"^([A-Za-z_][A-Za-z0-9_]*)\s*"
                r"(>=|<=|!=|<>|=|>|<)\s*(.*)$",
                condition
            )

            if not operator_match:

                errors.append(
                    f"Unsupported filter condition: "
                    f"{condition}"
                )

                continue

            field = operator_match.group(1).strip()
            operator = operator_match.group(2).strip()
            value = operator_match.group(3).strip()

            # ------------------------------------------
            # Validate operator
            # ------------------------------------------

            if operator not in supported_operators:

                errors.append(
                    f"Unsupported WHERE operator: "
                    f"'{operator}'."
                )

            # ------------------------------------------
            # Validate field
            # ------------------------------------------

            if field not in dimension_names:

                errors.append(
                    f"Filter field '{field}' "
                    f"is not a valid dimension."
                )

            # ------------------------------------------
            # Validate value
            # ------------------------------------------

            if not value:

                errors.append(
                    f"Filter value for '{field}' "
                    f"cannot be empty."
                )

    # ==================================================
    # Aggregation Validation
    # ==================================================

    def _validate_aggregations(
        self,
        sql,
        metric_names,
        dimension_names,
        errors
    ):

        upper_sql = sql.upper()

        supported_aggregations = {
            "SUM",
            "AVG",
            "MIN",
            "MAX",
            "COUNT"
        }

        # ----------------------------------------------
        # Find aggregation expressions
        # ----------------------------------------------

        import re

        aggregation_pattern = (
            r"\b(SUM|AVG|MIN|MAX|COUNT)\s*\(\s*"
            r"([A-Za-z_][A-Za-z0-9_]*)\s*\)"
        )

        matches = re.findall(
            aggregation_pattern,
            sql,
            re.IGNORECASE
        )

        # ----------------------------------------------
        # Validate each aggregation
        # ----------------------------------------------

        for aggregation, metric_name in matches:

            aggregation = aggregation.upper()

            # ------------------------------------------
            # Validate aggregation function
            # ------------------------------------------

            if aggregation not in supported_aggregations:

                errors.append(
                    f"Unsupported aggregation: "
                    f"{aggregation}"
                )

                continue

            # ------------------------------------------
            # Validate metric
            # ------------------------------------------

            if metric_name not in metric_names:

                errors.append(
                    f"Aggregation references unknown "
                    f"metric: '{metric_name}'."
                )

            if metric_name in dimension_names:

                errors.append(
                    f"Aggregation cannot be applied "
                    f"to dimension: '{metric_name}'."
                )

    # ==================================================
    # SELECT Expression Validation
    # ==================================================

    def _validate_select_expressions(
        self,
        sql,
        metric_names,
        dimension_names,
        errors
    ):

        import re

        # ----------------------------------------------
        # Extract SELECT clause
        # ----------------------------------------------

        match = re.search(
            r"^\s*SELECT\s+(.*?)\s+FROM\s+",
            sql,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return

        select_clause = match.group(1).strip()

        # ----------------------------------------------
        # Split SELECT expressions
        # ----------------------------------------------

        expressions = [
            expression.strip()
            for expression in select_clause.split(",")
        ]

        for expression in expressions:

            # ------------------------------------------
            # Remove optional alias
            # ------------------------------------------

            expression_without_alias = re.sub(
                r"\s+AS\s+[A-Za-z_][A-Za-z0-9_]*\s*$",
                "",
                expression,
                flags=re.IGNORECASE
            ).strip()

            # ------------------------------------------
            # Simple dimension
            # ------------------------------------------

            if expression_without_alias in dimension_names:
                continue

            # ------------------------------------------
            # Aggregated metric
            # ------------------------------------------

            aggregation_match = re.fullmatch(
                r"(SUM|AVG|MIN|MAX|COUNT)\s*\(\s*"
                r"([A-Za-z_][A-Za-z0-9_]*)\s*\)",
                expression_without_alias,
                re.IGNORECASE
            )

            if aggregation_match:

                metric_name = aggregation_match.group(2)

                if metric_name in metric_names:
                    continue

                # Already handled by aggregation validation.
                continue

            # ------------------------------------------
            # Unknown SELECT expression
            # ------------------------------------------

            errors.append(
                f"Invalid SELECT expression: "
                f"'{expression}'."
            )

    # ==================================================
    # WHERE Operator Validation
    # ==================================================

    def _validate_where_operators(
        self,
        sql,
        errors
    ):

        import re

        # ----------------------------------------------
        # Extract WHERE clause
        # ----------------------------------------------

        match = re.search(
            r"\bWHERE\b(.*?)(?:\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|$)",
            sql,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return

        where_clause = match.group(1).strip()

        if not where_clause:
            errors.append(
                "WHERE clause cannot be empty."
            )
            return

        # ----------------------------------------------
        # Split multiple conditions
        # ----------------------------------------------

        conditions = re.split(
            r"\s+AND\s+",
            where_clause,
            flags=re.IGNORECASE
        )

        supported_operators = {
            "=",
            "!=",
            "<>",
            ">",
            "<",
            ">=",
            "<="
        }

        for condition in conditions:

            condition = condition.strip()

            if not condition:
                errors.append(
                    "Empty WHERE condition."
                )
                continue

            # ------------------------------------------
            # Extract field/operator/value
            # ------------------------------------------

            operator_match = re.search(
                r"^(?:[A-Za-z_][A-Za-z0-9_]*)\s*"
                r"(>=|<=|!=|<>|=|>|<)\s*(.*)$",
                condition
            )

            if not operator_match:

                errors.append(
                    f"Invalid WHERE condition: "
                    f"'{condition}'."
                )

                continue

            operator = operator_match.group(1)
            value = operator_match.group(2).strip()

            # ------------------------------------------
            # Validate operator
            # ------------------------------------------

            if operator not in supported_operators:

                errors.append(
                    f"Unsupported WHERE operator: "
                    f"'{operator}'."
                )

            # ------------------------------------------
            # Validate value
            # ------------------------------------------

           # if not value:

            #    errors.append(
             #       "WHERE condition value "
              #      "cannot be empty."
               # )

    # ==================================================
    # HAVING Validation
    # ==================================================

    def _validate_having(
        self,
        sql,
        metric_names,
        dimension_names,
        errors
    ):

        import re

        # ----------------------------------------------
        # Extract HAVING clause
        # ----------------------------------------------

        match = re.search(
            r"\bHAVING\b(.*?)(?:\bORDER\s+BY\b|\bLIMIT\b|$)",
            sql,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return

        having_clause = match.group(1).strip()

        if not having_clause:

            errors.append(
                "HAVING clause cannot be empty."
            )

            return

        # ----------------------------------------------
        # Split multiple conditions
        # ----------------------------------------------

        conditions = re.split(
            r"\s+AND\s+",
            having_clause,
            flags=re.IGNORECASE
        )

        # ----------------------------------------------
        # Supported operators
        # ----------------------------------------------

        supported_operators = {
            "=",
            "!=",
            "<>",
            ">",
            "<",
            ">=",
            "<="
        }

        # ----------------------------------------------
        # Validate each condition
        # ----------------------------------------------

        for condition in conditions:

            condition = condition.strip()

            if not condition:

                errors.append(
                    "Empty HAVING condition."
                )

                continue

            # ------------------------------------------
            # Extract aggregation/operator/value
            # ------------------------------------------

            aggregation_match = re.match(
                r"^(SUM|AVG|MIN|MAX|COUNT)"
                r"\s*\(\s*"
                r"([A-Za-z_][A-Za-z0-9_]*)"
                r"\s*\)\s*"
                r"(>=|<=|!=|<>|=|>|<)"
                r"\s*(.*)$",
                condition,
                re.IGNORECASE
            )

            if not aggregation_match:

                errors.append(
                    f"Invalid HAVING condition: "
                    f"'{condition}'."
                )

                continue

            aggregation = (
                aggregation_match.group(1).upper()
            )

            field = (
                aggregation_match.group(2)
            )

            operator = (
                aggregation_match.group(3)
            )

            value = (
                aggregation_match.group(4).strip()
            )

            # ------------------------------------------
            # Validate operator
            # ------------------------------------------

            if operator not in supported_operators:

                errors.append(
                    f"Unsupported HAVING operator: "
                    f"'{operator}'."
                )

            # ------------------------------------------
            # Dimension cannot be aggregated
            # ------------------------------------------

            if field in dimension_names:

                errors.append(
                    f"HAVING cannot aggregate "
                    f"dimension: '{field}'."
                )

                continue

            # ------------------------------------------
            # Metric must exist
            # ------------------------------------------

            if field not in metric_names:

                errors.append(
                    f"HAVING references unknown "
                    f"metric: '{field}'."
                )

                continue

            # ------------------------------------------
            # Value must exist
            # ------------------------------------------

            if not value:

                errors.append(
                    f"HAVING value for "
                    f"'{field}' cannot be empty."
                )

    # ==================================================
    # ORDER BY Validation
    # ==================================================

    def _validate_order_by(
        self,
        sql,
        metric_names,
        dimension_names,
        errors
    ):

        import re

        # ----------------------------------------------
        # Extract ORDER BY clause
        # ----------------------------------------------

        match = re.search(
            r"\bORDER\s+BY\b(.*?)(?:\bLIMIT\b|$)",
            sql,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return

        order_by_clause = match.group(1).strip()

        # ----------------------------------------------
        # Empty ORDER BY
        # ----------------------------------------------

        if not order_by_clause:

            errors.append(
                "ORDER BY clause cannot be empty."
            )

            return

        # ----------------------------------------------
        # Split multiple sort expressions
        # ----------------------------------------------

        expressions = re.split(
            r"\s*,\s*",
            order_by_clause
        )

        valid_directions = {
            "ASC",
            "DESC"
        }

        for expression in expressions:

            expression = expression.strip()

            if not expression:
                errors.append(
                    "Empty ORDER BY expression."
                )
                continue

            # ------------------------------------------
            # Extract field and direction
            # ------------------------------------------

            parts = expression.split()

            if len(parts) > 2:

                errors.append(
                    f"Invalid ORDER BY expression: "
                    f"'{expression}'."
                )

                continue

            field = parts[0]

            direction = (
                parts[1].upper()
                if len(parts) == 2
                else "ASC"
            )

            # ------------------------------------------
            # Validate identifier
            # ------------------------------------------

            if field not in (
                metric_names | dimension_names
            ):

                errors.append(
                    f"ORDER BY field '{field}' "
                    f"is not a valid metric or dimension."
                )

            # ------------------------------------------
            # Validate direction
            # ------------------------------------------

            if direction not in valid_directions:

                errors.append(
                    f"Invalid ORDER BY direction: "
                    f"'{direction}'."
                )

    # ==================================================
    # LIMIT Validation
    # ==================================================

    def _validate_limit(
        self,
        sql,
        errors
    ):

        import re

        # ----------------------------------------------
        # Extract LIMIT clause
        # ----------------------------------------------

        match = re.search(
            r"\bLIMIT\b(.*)$",
            sql,
            re.IGNORECASE | re.DOTALL
        )

        if not match:
            return

        limit_clause = match.group(1).strip()

        # ----------------------------------------------
        # Empty LIMIT
        # ----------------------------------------------

        if not limit_clause:

            errors.append(
                "LIMIT clause cannot be empty."
            )

            return

        # ----------------------------------------------
        # Remove trailing semicolon
        # ----------------------------------------------

        limit_clause = (
            limit_clause
            .rstrip(";")
            .strip()
        )

        # ----------------------------------------------
        # LIMIT must be a positive integer
        # ----------------------------------------------

        if not re.fullmatch(
            r"[0-9]+",
            limit_clause
        ):

            errors.append(
                f"Invalid LIMIT value: "
                f"'{limit_clause}'."
            )

            return

        limit_value = int(limit_clause)

        # ----------------------------------------------
        # LIMIT must be greater than zero
        # ----------------------------------------------

        if limit_value <= 0:

            errors.append(
                "LIMIT value must be greater than zero."
            )

    # ==================================================
    # SQL Security Validation
    # ==================================================

    def _validate_security(
        self,
        sql,
        errors
    ):

        import re

        normalized_sql = sql.strip()

        # ----------------------------------------------
        # Multiple statements
        # ----------------------------------------------

        statements = [
            statement.strip()
            for statement in normalized_sql.split(";")
            if statement.strip()
        ]

        if len(statements) > 1:

            errors.append(
                "Multiple SQL statements are not allowed."
            )

        # ----------------------------------------------
        # SQL comments
        # ----------------------------------------------

        if "--" in normalized_sql:

            errors.append(
                "SQL comments are not allowed."
            )

        if "/*" in normalized_sql or "*/" in normalized_sql:

            errors.append(
                "SQL block comments are not allowed."
            )

        # ----------------------------------------------
        # Forbidden operations
        # ----------------------------------------------

        forbidden_operations = {
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "REPLACE",
            "MERGE",
            "GRANT",
            "REVOKE"
        }

        for operation in forbidden_operations:

            if re.search(
                rf"\b{operation}\b",
                normalized_sql,
                re.IGNORECASE
            ):

                errors.append(
                    f"Forbidden SQL operation: "
                    f"{operation}"
                )

        # ----------------------------------------------
        # Dangerous execution constructs
        # ----------------------------------------------

        dangerous_constructs = [
            "EXEC",
            "EXECUTE",
            "XP_CMDSHELL",
            "LOAD_FILE",
            "INTO OUTFILE",
            "INTO DUMPFILE"
        ]

        for construct in dangerous_constructs:

            if re.search(
                rf"\b{re.escape(construct)}\b",
                normalized_sql,
                re.IGNORECASE
            ):

                errors.append(
                    f"Forbidden SQL construct: "
                    f"{construct}"
                )