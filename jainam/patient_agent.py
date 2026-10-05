"""
=========================================================
MedIntel360
Patient Agent
=========================================================

AI Agent for Patient Analytics.

Author : Jainam Gada
"""

import pandas as pd

from ai_engine.base_agent import BaseAgent


class PatientAgent(BaseAgent):

    """
    Patient Analytics AI Agent.
    """


    # =====================================================
    # Dataset Summary
    # =====================================================

    def get_summary(self):

        return {

            "Total Admissions": int(self.df["admission_id"].nunique()),

            "Total Patients": int(self.df["patient_id"].nunique()),

            "Average LOS": float(round(self.df["los"].mean(), 2)),

            "Average Revenue": float(round(self.df["total_amount"].mean(), 2))

        }

    # =====================================================
    # AI Query Handler
    # =====================================================

    def answer(self, query: str):

        query = query.lower()

        if self.contains(query, "los", "length of stay"):

            return f"Average Length of Stay is {self.df['los'].mean():.2f} days."

        elif self.contains(query, "patient", "patients"):

            return f"Total Patients : {self.df['patient_id'].nunique()}"

        elif self.contains(query, "admission", "admissions"):

            return f"Total Admissions : {self.df['admission_id'].nunique()}"

        elif self.contains(query, "revenue", "income"):

            return f"Average Revenue per Admission : ₹{self.df['total_amount'].mean():,.2f}"

        else:

            return self.unknown_response()