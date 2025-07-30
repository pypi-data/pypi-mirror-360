"""
📊 Data Content Comparer Tool

This tool compares the content of two datasets and generates a detailed report
of their differences, including column differences, data type mismatches,
value discrepancies, and missing or extra rows.

Usage:
    Development: python -m scriptcraft.tools.data_content_comparer.main [args]
    Distributable: python main.py [args]
    Pipeline: Called via main_runner(**kwargs)
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

# === Environment Detection & Import Setup ===
# Import the environment detection module
from .env import setup_environment

# Set up environment and get imports
IS_DISTRIBUTABLE = setup_environment()

# Import based on environment
if IS_DISTRIBUTABLE:
    # Distributable imports - use cu pattern for consistency
    import common as cu
else:
    # Development imports - use cu pattern for consistency
    import scriptcraft.common as cu

# Import utils (same in both environments since it's local)
try:
    from .utils import (
        load_datasets_as_list, compare_datasets, generate_report, load_mode
    )
except ImportError:
    # If utils import fails, try current directory
    from .utils import (
        load_datasets_as_list, compare_datasets, generate_report, load_mode
    )


class DataContentComparer(cu.BaseTool):
    """Tool for comparing content between datasets."""
    
    def __init__(self):
        """Initialize the tool."""
        super().__init__(
            name="Data Content Comparer",
            description="📊 Compares content between datasets and generates detailed reports",
            tool_name="data_content_comparer"
        )
    
    def run(self,
            mode: Optional[str] = None,
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs) -> None:
        """
        Run the data content comparison.
        
        Args:
            mode: Comparison mode (e.g., 'full', 'quick', 'rhq_mode', 'standard_mode')
            input_paths: List containing paths to the datasets to compare
            output_dir: Directory to save comparison reports
            domain: Optional domain to filter comparison
            output_filename: Optional custom output filename
            **kwargs: Additional arguments:
                - comparison_type: Type of comparison to perform
                - output_format: Format for the output report
        """
        self.log_start()
        
        try:
            # Validate inputs using DRY method
            if not self.validate_input_files(input_paths or [], required_count=2):
                raise ValueError("❌ Need at least two input files to compare")
            
            # Resolve output directory using DRY method
            output_path = self.resolve_output_directory(output_dir or self.default_output_dir)
            
            # Get comparison settings
            comparison_type = kwargs.get('comparison_type', 'full')
            output_format = kwargs.get('output_format', 'excel')
            
            # Load datasets using DRY method
            cu.log_and_print("📂 Loading datasets...")
            df1 = self.load_data_file(input_paths[0])
            df2 = self.load_data_file(input_paths[1])
            
            # Use base class comparison method for basic analysis
            basic_comparison = self.compare_dataframes(df1, df2)
            
            # Perform detailed comparison using tool-specific logic
            cu.log_and_print("🔍 Performing detailed comparison...")
            detailed_comparison = compare_datasets(
                df1,
                df2,
                comparison_type=comparison_type,
                domain=domain
            )
            
            # Combine results
            comparison_results = {
                **basic_comparison,
                'detailed_analysis': detailed_comparison
            }
            
            # Generate output filename using DRY method
            if not output_filename:
                output_filename = self.get_output_filename(
                    input_paths[0], 
                    suffix=f"vs_{Path(input_paths[1]).stem}_comparison",
                    extension=f".{output_format}"
                )
            
            report_path = output_path / output_filename
            
            # Generate report
            cu.log_and_print("📄 Generating comparison report...")
            generate_report(
                comparison_results,
                report_path,
                format=output_format
            )
            
            self.log_completion(report_path)
            
        except Exception as e:
            self.log_error(f"Comparison failed: {e}")
            raise


def main():
    """Main entry point for the data content comparer tool."""
    args = cu.parse_tool_args("📊 Compares content between datasets and generates detailed reports")
    
    # Create and run the tool
    tool = DataContentComparer()
    tool.run(
        input_paths=args.input_paths,
        output_dir=args.output_dir,
        domain=args.domain,
        output_filename=args.output_filename,
        mode=args.mode
    )


if __name__ == "__main__":
    main() 