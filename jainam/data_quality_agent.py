import pandas as pd
from ai_engine.base_agent import BaseAgent


class DataQualityAgent(BaseAgent):

    def get_summary(self):

        return {

            "Rows": self.total_rows(),

            "Columns": self.total_columns(),

            "Missing Values": self.missing_values()

        }

    def answer(self, query):

        if self.contains(query, "missing", "null"):

            return f"Missing Values : {self.missing_values()}"

        elif self.contains(query, "rows"):

            return f"Rows : {self.total_rows()}"

        elif self.contains(query, "columns"):

            return f"Columns : {self.total_columns()}"

        else:

            return self.unknown_response()