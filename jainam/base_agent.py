"""
=========================================================
MedIntel360
Base Agent
=========================================================


Base class for all AI agents.

Author : Jainam Gada
"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseAgent(ABC):

    """
    Parent class for all MedIntel360 AI Agents.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame | None = None
    ):

        self.df = dataframe

    # =====================================================
    # Common Helpers
    # =====================================================

    @staticmethod
    def contains(query: str, *keywords):

        query = query.lower()

        return any(
            keyword.lower() in query
            for keyword in keywords
        )

    # -----------------------------------------------------

    def unknown_response(self):

        return (
            f"{self.__class__.__name__} "
            "could not understand the query."
        )

    # -----------------------------------------------------

    def total_rows(self):

        if self.df is None:

            raise RuntimeError(
                "DataFrame is not available "
                "for this agent."
            )

        return len(self.df)

    # -----------------------------------------------------

    def total_columns(self):

        if self.df is None:

            raise RuntimeError(
                "DataFrame is not available "
                "for this agent."
            )

        return len(self.df.columns)

    # -----------------------------------------------------

    def missing_values(self):

        if self.df is None:

            raise RuntimeError(
                "DataFrame is not available "
                "for this agent."
            )

        return int(
            self.df.isna().sum().sum()
        )

    # =====================================================
    # Abstract Methods
    # =====================================================

    @abstractmethod
    def get_summary(self):

        pass

    # -----------------------------------------------------

    @abstractmethod
    def answer(self, query: str):

        pass