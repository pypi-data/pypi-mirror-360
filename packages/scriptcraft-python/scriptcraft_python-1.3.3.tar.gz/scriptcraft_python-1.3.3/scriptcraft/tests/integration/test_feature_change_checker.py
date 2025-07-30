"""Integration tests for the feature change checker."""

import pytest
import pandas as pd
from pathlib import Path
from scriptcraft.tools.feature_change_checker import checker

def test_full_change_tracking_workflow(sample_paths, temp_output_dir) -> None:
    """Test the complete change tracking workflow."""
    # Create test data
    df = pd.DataFrame({
        "Med_ID": [1, 1, 2, 2],
        "Visit_ID": [1, 2, 1, 2],
        "CDX_Cog": [0, 1, 1, 2]
    })
    
    # Save test file
    data_path = temp_output_dir / "clinical_final.csv"
    df.to_csv(data_path, index=False)
    
    # Update paths
    paths = sample_paths.copy()
    paths["merged_data"] = str(temp_output_dir)
    
    # Run checker
    checker.check(
        domain="Clinical",
        input_path="",  # Not used directly
        output_path="", # Not used directly
        paths=paths
    )
    
    # Verify results
    results_path = Path(paths["qc_output"]) / "CDX_Cog_Category_Changes.csv"
    assert results_path.exists()
    results = pd.read_csv(results_path)
    assert not results.empty
    assert "Category" in results.columns