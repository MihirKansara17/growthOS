import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.db.models import Customer, Transaction
import datetime

class RFMEngine:
    @staticmethod
    def calculate_rfm(db: Session, tenant_id: str):
        tenant_customers = db.query(Customer).filter(Customer.tenant_id == tenant_id).all()
        if not tenant_customers:
            return {"status": "NO_CUSTOMER_DATA", "message": "Tenant does not have customer phone/ID tracking enabled."}

        now = datetime.datetime.utcnow()
        txs = db.query(Transaction).filter(
            Transaction.tenant_id == tenant_id,
            Transaction.customer_id.isnot(None)
        ).all()

        if not txs:
            return {"status": "NO_TRANSACTIONS", "message": "No customer-linked transactions found."}

        df_tx = pd.DataFrame([{
            "customer_id": t.customer_id,
            "timestamp": t.timestamp,
            "amount": t.total_amount
        } for t in txs])

        rfm = df_tx.groupby("customer_id").agg({
            "timestamp": lambda x: (now - x.max()).days, # Recency in days
            "customer_id": "count",                      # Frequency
            "amount": "sum"                              # Monetary
        }).rename(columns={"timestamp": "recency", "customer_id": "frequency", "amount": "monetary"}).reset_index()

        # Classify customer segments
        def classify_segment(row):
            if row["recency"] > 60:
                return "At-Risk / Churn Warning"
            elif row["frequency"] >= 5 and row["monetary"] >= 5000:
                return "VIP Champions"
            elif row["recency"] <= 30:
                return "Active Loyal"
            else:
                return "Standard"

        rfm["segment"] = rfm.apply(classify_segment, axis=1)
        segment_counts = rfm["segment"].value_counts().to_dict()

        total_custs = len(rfm)
        segments_summary = [
            {"segment": k, "count": int(v), "percentage": round((v / total_custs) * 100, 1)}
            for k, v in segment_counts.items()
        ]

        at_risk_list = rfm[rfm["segment"] == "At-Risk / Churn Warning"].head(10).to_dict(orient="records")

        return {
            "tenant_id": tenant_id,
            "total_tracked_customers": total_custs,
            "average_recency_days": round(float(rfm["recency"].mean()), 1),
            "average_frequency": round(float(rfm["frequency"].mean()), 1),
            "average_monetary": round(float(rfm["monetary"].mean()), 2),
            "segments": segments_summary,
            "top_at_risk_customers": at_risk_list
        }
