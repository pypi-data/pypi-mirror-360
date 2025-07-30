"""Integration tests for the release consistency checker."""

import pytest
import pandas as pd
from pathlib import Path
from scriptcraft.tools.release_consistency_checker import checker

def test_full_consistency_check_workflow(sample_paths, temp_output_dir) -> None:
    """Test the complete consistency check workflow."""
    # Create test data
    r5_data = pd.DataFrame({
        "Med_ID": [1, 1, 2, 2],
        "Visit_ID": [1, 2, 1, 2],
        "Value_A": [10, 20, 30, 40],
        "Old_Col": [1, 2, 3, 4]
    })
    
    r6_data = pd.DataFrame({
        "Med_ID": [1, 1, 2, 2],
        "Visit_ID": [1, 2, 1, 2],
        "Value_A": [10, 25, 30, 45],  # Changed values
        "New_Col": [5, 6, 7, 8]       # New column
    })
    
    # Create test files
    r5_path = temp_output_dir / "domains/Clinical/HD Release 5 Clinical.csv"
    r6_path = temp_output_dir / "domains/Clinical/HD Release 6 Clinical_FINAL.csv"
    
    r5_path.parent.mkdir(parents=True, exist_ok=True)
    r6_path.parent.mkdir(parents=True, exist_ok=True)
    
    r5_data.to_csv(r5_path, index=False)
    r6_data.to_csv(r6_path, index=False)
    
    # Run checker
    checker.check(
        domain="Clinical",
        input_path="",  # Not used directly
        output_path="", # Not used directly
        paths=sample_paths
    )
    
    # Verify results
    results_path = Path(sample_paths["qc_output"]) / "Clinical_changed_rows.csv"
    assert results_path.exists()
    results = pd.read_csv(results_path)
    assert not results.empty
    
def test_manual_comparison_workflow(temp_output_dir) -> None:
    """Test the manual file comparison workflow."""
    # Create test data
    file1 = pd.DataFrame({
        "Med_ID": [1, 2],
        "Value": [10, 20]
    })
    file2 = pd.DataFrame({
        "Med_ID": [1, 2],
        "Value": [10, 25]  # One value changed
    })
    
    # Save test files
    path1 = temp_output_dir / "file1.csv"
    path2 = temp_output_dir / "file2.csv"
    file1.to_csv(path1, index=False)
    file2.to_csv(path2, index=False)
    
    # Run manual comparison
    checker.check_manual(
        r5_filename=str(path1),
        r6_filename=str(path2),
        debug=True,
        mode="standard"
    )
    
    # Verify results
    results = list(temp_output_dir.glob("*_changed_rows.csv"))
    assert len(results) > 0