"""Integration tests for the dictionary driven checker."""

import pytest
import pandas as pd
from pathlib import Path
from scriptcraft.tools.dictionary_driven_checker import checker

def test_full_validation_workflow(sample_paths, temp_output_dir) -> None:
    """Test the complete validation workflow."""
    # Create test data
    df = pd.DataFrame({
        "ID": [1, 2, 3],
        "Value": ["A", "B", "C"]
    })
    dict_df = pd.DataFrame({
        "Column": ["ID", "Value"],
        "Type": ["int", "str"],
        "Allowed_Values": ["", "A,B,C"]
    })
    
    # Save test files
    data_path = temp_output_dir / "test_data.csv"
    dict_path = temp_output_dir / "Clinical_dictionary.csv"
    df.to_csv(data_path, index=False)
    dict_df.to_csv(dict_path, index=False)
    
    # Run checker
    checker.check(
        domain="Clinical",
        input_path=str(data_path),
        output_path=str(temp_output_dir / "results.csv"),
        paths=sample_paths
    )
    
    # Verify results
    results_path = temp_output_dir / "results.csv"
    assert results_path.exists()
    results = pd.read_csv(results_path)
    assert not results.empty