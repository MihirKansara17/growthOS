import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.db.models import InventorySnapshot, Product, TransactionItem, Transaction, Store
import datetime

class InventoryEngine:
    @staticmethod
    def get_inventory_health(db: Session, tenant_id: str, days: int = 30):
        snapshots = db.query(InventorySnapshot).filter(InventorySnapshot.tenant_id == tenant_id).all()
        if not snapshots:
            return {"status": "NO_INVENTORY_DATA", "message": "Tenant does not have SKU/Inventory stock tracking enabled."}

        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        items = db.query(TransactionItem).join(Transaction).filter(
            Transaction.tenant_id == tenant_id,
            Transaction.timestamp >= cutoff
        ).all()

        # Compute sales velocity per product
        sales_qty = {}
        for item in items:
            sales_qty[item.product_id] = sales_qty.get(item.product_id, 0) + item.quantity

        inventory_report = []
        stockout_risk_count = 0
        overstock_count = 0

        for snap in snapshots:
            prod = db.query(Product).filter(Product.id == snap.product_id).first()
            store = db.query(Store).filter(Store.id == snap.store_id).first()
            if not prod or not store:
                continue

            total_sold_30d = sales_qty.get(prod.id, 0)
            daily_velocity = total_sold_30d / float(days) if total_sold_30d > 0 else 0.05
            days_of_cover = snap.stock_on_hand / daily_velocity

            is_stockout_risk = days_of_cover < 7
            is_overstock = days_of_cover > 60

            if is_stockout_risk:
                stockout_risk_count += 1
            if is_overstock:
                overstock_count += 1

            inventory_report.append({
                "product_id": prod.id,
                "product_name": prod.name,
                "category": prod.category,
                "store_name": store.name,
                "stock_on_hand": snap.stock_on_hand,
                "reorder_level": snap.reorder_level,
                "daily_velocity": round(daily_velocity, 2),
                "days_of_cover": round(days_of_cover, 1),
                "status": "STOCKOUT_RISK" if is_stockout_risk else ("OVERSTOCK" if is_overstock else "HEALTHY"),
                "recommended_reorder_qty": max(0, int((15 * daily_velocity) - snap.stock_on_hand)) if is_stockout_risk else 0
            })

        return {
            "tenant_id": tenant_id,
            "total_items_tracked": len(inventory_report),
            "stockout_risk_items_count": stockout_risk_count,
            "overstock_items_count": overstock_count,
            "items": sorted(inventory_report, key=lambda x: x["days_of_cover"])
        }
