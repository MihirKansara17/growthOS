from sqlalchemy.orm import Session
from typing import Dict, Any, Tuple
from app.engine.kpi_engine import KPIEngine
from app.engine.root_cause import RootCauseEngine
from app.engine.rfm_engine import RFMEngine
from app.engine.inventory_engine import InventoryEngine
# Simulator could be added here later

class EngineExecutor:
    """Routes the selected tool to the actual deterministic backend engine."""
    
    def execute(self, db: Session, tenant_id: str, selected_tool: str, validated_args: Dict[str, Any]) -> Tuple[bool, Any, str]:
        """
        Returns: (success, result_data, error_message)
        """
        try:
            if selected_tool == "get_business_health":
                # Assuming KPIEngine returns a dict with health_score etc.
                result = KPIEngine.calculate_summary(db, tenant_id)
                return True, result, ""

            elif selected_tool == "get_revenue_summary":
                result = KPIEngine.calculate_summary(db, tenant_id)
                return True, result, ""

            elif selected_tool == "get_revenue_breakdown":
                result = RootCauseEngine.analyze_variance(db, tenant_id)
                return True, result, ""

            elif selected_tool == "get_customer_segments":
                result = RFMEngine.calculate_rfm(db, tenant_id)
                return True, result, ""

            elif selected_tool == "get_inventory_risk":
                result = InventoryEngine.get_inventory_health(db, tenant_id)
                return True, result, ""

            else:
                return False, None, f"Tool '{selected_tool}' is valid in schema but not implemented in Executor."
                
        except Exception as e:
            return False, None, f"Execution failed for '{selected_tool}': {str(e)}"
