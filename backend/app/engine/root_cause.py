import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.db.models import Transaction, TransactionItem, Store, Product
import datetime

class RootCauseEngine:
    @staticmethod
    def analyze_variance(db: Session, tenant_id: str, days: int = 30):
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        prev_cutoff = cutoff - datetime.timedelta(days=days)

        curr_txs = db.query(Transaction).filter(
            Transaction.tenant_id == tenant_id,
            Transaction.timestamp >= cutoff
        ).all()

        prev_txs = db.query(Transaction).filter(
            Transaction.tenant_id == tenant_id,
            Transaction.timestamp >= prev_cutoff,
            Transaction.timestamp < cutoff
        ).all()

        curr_rev = sum(t.total_amount for t in curr_txs)
        prev_rev = sum(t.total_amount for t in prev_txs) or 1.0
        diff_rev = curr_rev - prev_rev

        curr_vol = len(curr_txs)
        prev_vol = len(prev_txs) or 1
        curr_aov = curr_rev / curr_vol if curr_vol > 0 else 0
        prev_aov = prev_rev / prev_vol if prev_vol > 0 else 0

        # Variance decomposition: Revenue change = Volume effect + Price/Mix effect
        volume_effect = (curr_vol - prev_vol) * prev_aov
        price_mix_effect = curr_vol * (curr_aov - prev_aov)

        # Store breakdown driver
        stores = db.query(Store).filter(Store.tenant_id == tenant_id).all()
        store_drivers = []
        for s in stores:
            s_curr = sum(t.total_amount for t in curr_txs if t.store_id == s.id)
            s_prev = sum(t.total_amount for t in prev_txs if t.store_id == s.id) or 1.0
            s_diff = s_curr - s_prev
            store_drivers.append({
                "store_id": s.id,
                "store_name": s.name,
                "impact_amount": round(s_diff, 2),
                "growth_pct": round(((s_curr - s_prev) / s_prev) * 100, 1)
            })

        # Category breakdown driver
        curr_items = db.query(TransactionItem).join(Transaction).filter(
            Transaction.tenant_id == tenant_id, Transaction.timestamp >= cutoff
        ).all()
        prev_items = db.query(TransactionItem).join(Transaction).filter(
            Transaction.tenant_id == tenant_id, Transaction.timestamp >= prev_cutoff, Transaction.timestamp < cutoff
        ).all()

        cat_curr = {}
        for item in curr_items:
            cat_curr[item.category_name] = cat_curr.get(item.category_name, 0) + item.total_price

        cat_prev = {}
        for item in prev_items:
            cat_prev[item.category_name] = cat_prev.get(item.category_name, 0) + item.total_price

        all_cats = set(cat_curr.keys()).union(set(cat_prev.keys()))
        category_drivers = []
        for c in all_cats:
            c_c = cat_curr.get(c, 0)
            c_p = cat_prev.get(c, 0)
            diff = c_c - c_p
            category_drivers.append({
                "category": c,
                "impact_amount": round(diff, 2),
                "growth_pct": round(((c_c - c_p) / (c_p or 1)) * 100, 1)
            })

        return {
            "evidence_id": f"ev_rca_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M')}",
            "period_days": days,
            "total_variance": round(diff_rev, 2),
            "variance_pct": round((diff_rev / prev_rev) * 100, 2),
            "volume_effect": round(volume_effect, 2),
            "price_mix_effect": round(price_mix_effect, 2),
            "store_drivers": sorted(store_drivers, key=lambda x: abs(x["impact_amount"]), reverse=True),
            "category_drivers": sorted(category_drivers, key=lambda x: abs(x["impact_amount"]), reverse=True),
            "primary_diagnosis": (
                "Revenue variance was driven primarily by Volume change."
                if abs(volume_effect) > abs(price_mix_effect)
                else "Revenue variance was driven primarily by Average Order Value / Product Mix shifts."
            )
        }
