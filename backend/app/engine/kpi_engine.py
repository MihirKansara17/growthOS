import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Transaction, TransactionItem, Product, Store
import datetime

class KPIEngine:
    @staticmethod
    def calculate_summary(db: Session, tenant_id: str, days: int = 30):
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        prev_cutoff = cutoff - datetime.timedelta(days=days)

        # Current period transactions
        txs_curr = db.query(Transaction).filter(
            Transaction.tenant_id == tenant_id,
            Transaction.timestamp >= cutoff
        ).all()

        # Previous period transactions for growth metrics
        txs_prev = db.query(Transaction).filter(
            Transaction.tenant_id == tenant_id,
            Transaction.timestamp >= prev_cutoff,
            Transaction.timestamp < cutoff
        ).all()

        total_rev_curr = sum(t.total_amount for t in txs_curr)
        total_rev_prev = sum(t.total_amount for t in txs_prev) or 1.0

        num_tx_curr = len(txs_curr)
        num_tx_prev = len(txs_prev) or 1

        aov_curr = total_rev_curr / num_tx_curr if num_tx_curr > 0 else 0
        aov_prev = total_rev_prev / num_tx_prev if num_tx_prev > 0 else 0

        rev_growth = ((total_rev_curr - total_rev_prev) / total_rev_prev) * 100
        aov_growth = ((aov_curr - aov_prev) / aov_prev) * 100 if aov_prev > 0 else 0

        # Health score calculation (0 - 100) based on growth, transaction volume & stability
        health_score = int(np.clip(75 + (rev_growth * 0.4), 40, 98))

        # Daily sales trend
        daily_sales = {}
        for t in txs_curr:
            date_str = t.timestamp.strftime("%Y-%m-%d")
            daily_sales[date_str] = daily_sales.get(date_str, 0) + t.total_amount

        trend_data = [{"date": k, "revenue": round(v, 2)} for k, v in sorted(daily_sales.items())]

        return {
            "tenant_id": tenant_id,
            "period_days": days,
            "health_score": health_score,
            "total_revenue": round(total_rev_curr, 2),
            "revenue_growth_pct": round(rev_growth, 2),
            "total_transactions": num_tx_curr,
            "average_order_value": round(aov_curr, 2),
            "aov_growth_pct": round(aov_growth, 2),
            "daily_trend": trend_data
        }

    @staticmethod
    def category_breakdown(db: Session, tenant_id: str, days: int = 30):
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        items = db.query(TransactionItem).join(Transaction).filter(
            Transaction.tenant_id == tenant_id,
            Transaction.timestamp >= cutoff
        ).all()

        cat_summary = {}
        for item in items:
            cat = item.category_name or "General"
            cat_summary[cat] = cat_summary.get(cat, 0) + item.total_price

        total = sum(cat_summary.values()) or 1.0
        result = [
            {"category": k, "revenue": round(v, 2), "share_pct": round((v / total) * 100, 1)}
            for k, v in cat_summary.items()
        ]
        return sorted(result, key=lambda x: x["revenue"], reverse=True)
