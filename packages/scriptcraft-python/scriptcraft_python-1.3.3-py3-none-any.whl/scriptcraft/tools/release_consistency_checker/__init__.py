"""
🔄 Release Consistency Checker Tool

Checks consistency between different data releases to ensure data integrity.
Identifies changes, inconsistencies, and potential issues across releases.

Features:
- 🔄 Release-to-release comparison
- 📊 Consistency analysis
- 📋 Change tracking and reporting
- 🔍 Data integrity validation
- 📈 Statistical summaries
- ⚠️ Inconsistency detection

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .utils import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'ReleaseConsistencyChecker'
# ]

# Tool metadata
__description__ = "🔄 Checks consistency between different data releases to ensure data integrity"
__tags__ = ["consistency", "releases", "comparison", "validation", "integrity"]
__data_types__ = ["csv", "xlsx", "xls"]
__domains__ = ["clinical", "biomarkers", "genomics", "imaging"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "pipeline"
