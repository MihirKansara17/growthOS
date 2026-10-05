import requests
import json
from sqlalchemy.orm import Session
from app.core.config import settings
from app.engine.kpi_engine import KPIEngine
from app.engine.root_cause import RootCauseEngine
from app.engine.rfm_engine import RFMEngine
from app.engine.inventory_engine import InventoryEngine
from app.engine.simulator import SimulatorEngine

class AIOrchestrator:
    @staticmethod
    def ask_growthos(db: Session, tenant_id: str, prompt: str):
        # 1. Execute backend analytics engines to build grounded evidence object
        kpi_data = KPIEngine.calculate_summary(db, tenant_id)
        rca_data = RootCauseEngine.analyze_variance(db, tenant_id)
        rfm_data = RFMEngine.calculate_rfm(db, tenant_id)
        inv_data = InventoryEngine.get_inventory_health(db, tenant_id)

        evidence_context = {
            "tenant_id": tenant_id,
            "kpi_summary": kpi_data,
            "root_cause_analysis": rca_data,
            "customer_rfm": rfm_data,
            "inventory_health": {
                "stockout_items_count": inv_data.get("stockout_risk_items_count", 0),
                "overstock_items_count": inv_data.get("overstock_items_count", 0)
            }
        }

        # 2. Check if user provided an OpenRouter API key
        if settings.OPENROUTER_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://growthos-retail.com",
                    "X-Title": "GrowthOS Retail Intelligence"
                }
                system_prompt = (
                    "You are GrowthOS, an expert AI decision intelligence assistant for Indian retail businesses. "
                    "You MUST stay strictly grounded in the provided business evidence JSON below. "
                    "Do NOT invent unverified numbers. Explain key metrics, diagnose causes, and give clear, evidence-backed retail advice."
                )
                payload = {
                    "model": settings.OPENROUTER_MODEL,
                    "messages": [
                        {"role": "system", "content": f"{system_prompt}\nEVIDENCE JSON:\n{json.dumps(evidence_context)}"},
                        {"role": "user", "content": prompt}
                    ]
                }
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data["choices"][0]["message"]["content"]
                    return {
                        "mode": "OPENROUTER_LIVE_LLM",
                        "model": settings.OPENROUTER_MODEL,
                        "answer": answer,
                        "evidence": evidence_context
                    }
            except Exception as e:
                print(f"OpenRouter API error fallback: {e}")

        # 3. Deterministic Grounded Fallback Engine (Runs offline / keyless)
        lower_p = prompt.lower()
        if "revenue" in lower_p or "sales" in lower_p or "drop" in lower_p or "why" in lower_p:
            answer = (
                f"**Revenue Diagnosis for {tenant_id}**:\n\n"
                f"- **Total 30-Day Revenue**: ₹{kpi_data['total_revenue']:,} ({kpi_data['revenue_growth_pct']}% YoY/MoM growth).\n"
                f"- **Root Cause Diagnosis**: {rca_data['primary_diagnosis']}\n"
                f"- **Volume vs Price Impact**: Volume effect: ₹{rca_data['volume_effect']:,} | Price/Mix effect: ₹{rca_data['price_mix_effect']:,}.\n"
                f"- **Top Impacted Category**: {rca_data['category_drivers'][0]['category']} (₹{rca_data['category_drivers'][0]['impact_amount']:,}).\n\n"
                f"**Recommended Action**: Review pricing & promotional discounts on top volume categories."
            )
        elif "stock" in lower_p or "inventory" in lower_p or "reorder" in lower_p:
            answer = (
                f"**Inventory Health Report**:\n\n"
                f"- **Critical Stockout Risk Items**: {inv_data.get('stockout_risk_items_count', 0)} items have Days of Cover < 7 days.\n"
                f"- **Overstocked Items**: {inv_data.get('overstock_items_count', 0)} items have Days of Cover > 60 days.\n\n"
                f"**Recommended Action**: Reorder stock for critical items immediately to prevent lost sales."
            )
        else:
            answer = (
                f"**GrowthOS Business Overview**:\n\n"
                f"- **Business Health Score**: {kpi_data['health_score']}/100\n"
                f"- **30-Day Revenue**: ₹{kpi_data['total_revenue']:,}\n"
                f"- **Average Order Value (AOV)**: ₹{kpi_data['average_order_value']}\n"
                f"- **Customer Segments**: Active RFM tracking with {rfm_data.get('total_tracked_customers', 0)} customers.\n\n"
                f"Ask me specific questions about revenue drops, inventory stockout risks, or RFM churn!"
            )

        return {
            "mode": "DETERMINISTIC_GROUNDED_ENGINE",
            "model": "GrowthOS Grounded Rule Engine",
            "answer": answer,
            "evidence": evidence_context
        }
