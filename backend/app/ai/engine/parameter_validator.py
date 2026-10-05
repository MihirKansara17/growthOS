from typing import Dict, Any, Tuple
from app.ai.engine.metadata_manager import MetadataManager
from app.ai.engine.data_understanding_agent import DataUnderstandingResult

class ParameterValidator:
    def __init__(self, metadata: MetadataManager):
        self.metadata = metadata

    def validate(self, understanding_result: DataUnderstandingResult) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validates the chosen tool and constructs safe arguments for the backend engine.
        Returns: (is_valid, error_message, validated_args)
        """
        selected_tool = understanding_result.selected_tool

        if not selected_tool:
            return False, "No tool selected.", {}

        valid_tools = self.metadata.get_tool_names()
        if selected_tool not in valid_tools:
            return False, f"Selected tool '{selected_tool}' is not recognized.", {}

        # Here we would normally validate required parameters per tool.
        # For GrowthOS MVP, most backend tools take (db, tenant_id) which is injected at execution.
        # We just pass along filters and timeframe cleanly.
        
        validated_args = {
            "timeframe": understanding_result.timeframe,
            "filters": understanding_result.filters
        }

        return True, "", validated_args
