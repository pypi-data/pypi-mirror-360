"""
ScriptCraft Tools Package

This package contains all tools for data processing, validation, transformation, and automation.
Tools are organized by functionality but all accessible through a unified interface.

Example Usage:
    from scriptcraft.tools import (
        # All tools are now available
        RHQFormAutofiller, DataContentComparer, SchemaDetector, 
        DictionaryDrivenChecker, ReleaseConsistencyChecker, ScoreTotalsChecker,
        FeatureChangeChecker, DictionaryValidator, MedVisitIntegrityValidator,
        DictionaryCleaner, DateFormatStandardizer, AutomatedLabeler
    )

Tool Discovery:
    from scriptcraft.tools import get_available_tools, list_tools_by_category
    
    # Get all tools
    tools = get_available_tools()
    
    # Get tools by category
    validation_tools = list_tools_by_category("validation")
"""

# Import the unified registry system from the new registry package
from scriptcraft.common.registry import (
    get_available_tools,
    list_tools_by_category,
    discover_tool_metadata,
    registry
)

# Convenience function for backward compatibility
def get_tool_categories() -> list:
    """Get list of available tool categories."""
    return list(registry.get_tools_by_category().keys())

# Convenience function for running tools
def run_tool(tool_name: str, **kwargs) -> None:
    """Run a tool by name with the given arguments."""
    registry.run_tool(tool_name, **kwargs)

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .rhq_form_autofiller import *
from .data_content_comparer import *
from .schema_detector import *
from .dictionary_driven_checker import *
from .release_consistency_checker import *
from .score_totals_checker import *
from .feature_change_checker import *
from .dictionary_validator import *
from .medvisit_integrity_validator import *
from .dictionary_cleaner import *
from .date_format_standardizer import *
from .automated_labeler import *
from .dictionary_workflow import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'RHQFormAutofiller', 'DataContentComparer', 'SchemaDetector',
#     'DictionaryDrivenChecker', 'ReleaseConsistencyChecker', 'ScoreTotalsChecker',
#     'FeatureChangeChecker', 'DictionaryValidator', 'MedVisitIntegrityValidator',
#     'DictionaryCleaner', 'DateFormatStandardizer', 'AutomatedLabeler',
#     'DictionaryWorkflow',
#     'get_available_tools', 'list_tools_by_category', 'run_tool', 'discover_tool_metadata',
#     'get_tool_categories'
# ]
