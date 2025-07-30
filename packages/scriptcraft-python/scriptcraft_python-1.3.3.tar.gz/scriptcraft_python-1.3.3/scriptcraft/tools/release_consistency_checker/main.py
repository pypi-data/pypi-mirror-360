"""
Release Consistency Checker Tool

Validates data consistency between different releases of the same dataset.
"""

import sys
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

from scriptcraft.common.cli import parse_tool_args
from scriptcraft.common.logging import setup_logger
from scriptcraft.common.core.base import BaseTool
from scriptcraft.common import log_and_print
from .env import is_development_environment
from .utils import monitor_changes, DATASETS


class ReleaseConsistencyChecker(BaseTool):
    """Checker for validating consistency between different data releases."""
    
    def __init__(self):
        """Initialize the release consistency checker."""
        super().__init__(
            name="Release Consistency Checker",
            description="Validates consistency between different data releases",
            tool_name="release_consistency_checker"
        )
    
    def run(self, *args, **kwargs) -> None:
        """
        Run the release consistency checking process.
        
        Args:
            *args: Positional arguments (can include domains)
            **kwargs: Keyword arguments including:
                - domains: List of domains to process
                - output_dir: Output directory
                - debug: Enable debug mode
                - mode: Comparison mode
        """
        self.log_start()
        
        try:
            # Extract arguments
            domains = kwargs.get('domains') or (args[0] if args else None)
            output_dir = kwargs.get('output_dir', self.default_output_dir)
            debug = kwargs.get('debug', False)
            mode = kwargs.get('mode', 'old_only')
            
            # Validate inputs
            if not domains:
                # Default to all available domains from DATASETS
                domains = [d["dataset_name"] for d in DATASETS]
            
            if isinstance(domains, str):
                domains = [domains]
            
            # Resolve output directory
            output_path = self.resolve_output_directory(output_dir)
            
            # Process each domain
            for domain in domains:
                log_and_print(f"🔍 Processing domain: {domain}")
                
                # Process the domain
                self.process_domain(domain, None, None, output_path, 
                                  debug=debug, mode=mode, **kwargs)
            
            self.log_completion()
            
        except Exception as e:
            self.log_error(f"Release consistency checking failed: {e}")
            raise
    
    def process_domain(self, domain: str, dataset_file: Path, dictionary_file: Optional[Path], 
                      output_path: Path, **kwargs) -> None:
        """
        Check consistency between data releases.
        
        Args:
            domain: The domain to check (e.g., "Biomarkers", "Clinical")
            dataset_file: Not used directly (dataset config is used instead)
            dictionary_file: Not used for this tool
            output_path: Not used directly (dataset config is used instead)
            **kwargs: Additional arguments
        """
        dataset_config = next((d for d in DATASETS if d["dataset_name"] == domain), None)
        if not dataset_config:
            log_and_print(f"❌ No dataset config found for {domain}", level="error")
            return

        base_path = Path("domains")
        dataset_config["data_dir"] = str(base_path / domain)
        
        resolved_path = Path(dataset_config["data_dir"])
        log_and_print(f"🔍 Looking for data in: {resolved_path}")

        try:
            monitor_changes(**dataset_config)
        except Exception as e:
            log_and_print(f"❌ Error while processing {domain}: {e}", level="error")
            log_and_print(traceback.format_exc())
            raise
    
    def check_manual(
        self,
        r5_filename: str,
        r6_filename: str,
        debug: bool = False,
        mode: str = "old_only"
    ) -> None:
        """
        Run manual check between two specific files.
        
        Args:
            r5_filename: Path to R5 file
            r6_filename: Path to R6 file
            debug: Enable debug mode for dtype checks
            mode: Comparison mode ('old_only' or 'standard')
        """
        monitor_changes(
            dataset_name="Manual_Run",
            r5_filename=r5_filename,
            r6_filename=r6_filename,
            data_dir=".",  # Assume flat input folder
            debug=debug,
            mode=mode
        )


def main():
    """Main entry point for the release consistency checker tool."""
    args = parse_tool_args("Validates data consistency between different releases")
    logger = setup_logger("release_consistency_checker")
    
    # Create the tool
    tool = ReleaseConsistencyChecker()
    
    # Check if manual mode is requested
    if hasattr(args, 'input') and args.input:
        # Manual file comparison mode
        log_and_print("🛠 Running manual file comparison mode...")
        tool.check_manual(
            r5_filename=args.input[0],
            r6_filename=args.input[1],
            debug=getattr(args, 'debug', False),
            mode=getattr(args, 'mode', 'old_only')
        )
    else:
        # Standard domain mode
        tool.run(args)


if __name__ == "__main__":
    main() 