import numpy as np
from sqlalchemy.orm import Session
from app.db.models import Transaction
import datetime

class SimulatorEngine:
    @staticmethod
    def simulate_scenario(db: Session, tenant_id: str, discount_pct: float = 10.0, price_change_pct: float = 0.0, reorder_units: int = 100):
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        txs = db.query(Transaction).filter(
            Transaction.tenant_id == tenant_id,
            Transaction.timestamp >= cutoff
        ).all()

        current_30d_rev = sum(t.total_amount for t in txs) or 100000.0
        current_orders = len(txs) or 200
        avg_cost_ratio = 0.65 # Estimated 65% COGS for retail baseline

        # Elasticity assumptions: 10% discount -> 18% volume boost (Price elasticity of demand ~ -1.8)
        volume_change_pct = (discount_pct * 1.8) - (price_change_pct * 1.5)
        projected_orders = int(current_orders * (1 + (volume_change_pct / 100.0)))

        projected_aov = (current_30d_rev / current_orders) * (1 - (discount_pct / 100.0) + (price_change_pct / 100.0))
        projected_revenue = projected_orders * projected_aov

        current_cogs = current_30d_rev * avg_cost_ratio
        current_gross_margin = current_30d_rev - current_cogs

        projected_cogs = projected_revenue * avg_cost_ratio + (reorder_units * 150) # Estimated reorder cost
        projected_gross_margin = projected_revenue - projected_cogs

        revenue_impact = projected_revenue - current_30d_rev
        margin_impact = projected_gross_margin - current_gross_margin

        return {
            "tenant_id": tenant_id,
            "inputs": {
                "discount_pct": discount_pct,
                "price_change_pct": price_change_pct,
                "reorder_units": reorder_units
            },
            "baseline_30d_revenue": round(current_30d_rev, 2),
            "projected_30d_revenue": round(projected_revenue, 2),
            "revenue_impact_amount": round(revenue_impact, 2),
            "revenue_impact_pct": round((revenue_impact / current_30d_rev) * 100, 2),
            "baseline_gross_margin": round(current_gross_margin, 2),
            "projected_gross_margin": round(projected_gross_margin, 2),
            "margin_impact_amount": round(margin_impact, 2),
            "recommendation": (
                "PROCEED: Projected volume increase offsets discount margin contraction."
                if margin_impact >= 0
                else "CAUTION: Projected discount reduces overall gross profit despite volume increase."
            )
        }
