"""Performance tests for checker packages."""

import pytest
import pandas as pd
import time
from pathlib import Path
from scriptcraft.tools.dictionary_driven_checker import checker as dict_checker
from scriptcraft.tools.feature_change_checker import checker as feature_checker

def generate_large_dataset(rows=100000):
    """Generate a large test dataset."""
    return pd.DataFrame({
        "Med_ID": range(rows),
        "Visit_ID": [1] * rows,
        "CDX_Cog": [0, 1, 2] * (rows // 3 + 1),
        "Value": ["A", "B", "C"] * (rows // 3 + 1)
    })

@pytest.mark.performance
def test_dictionary_checker_performance(sample_paths, temp_output_dir) -> None:
    """Test dictionary checker performance with large dataset."""
    # Generate test data
    df = generate_large_dataset()
    dict_df = pd.DataFrame({
        "Column": ["Med_ID", "Visit_ID", "CDX_Cog", "Value"],
        "Type": ["int", "int", "int", "str"],
        "Allowed_Values": ["", "", "0,1,2", "A,B,C"]
    })
    
    # Save test files
    data_path = temp_output_dir / "large_data.csv"
    dict_path = temp_output_dir / "Clinical_dictionary.csv"
    df.to_csv(data_path, index=False)
    dict_df.to_csv(dict_path, index=False)
    
    # Measure performance
    start_time = time.time()
    dict_checker.check(
        domain="Clinical",
        input_path=str(data_path),
        output_path=str(temp_output_dir / "results.csv"),
        paths=sample_paths
    )
    duration = time.time() - start_time
    
    # Assert performance criteria
    assert duration < 60, f"Dictionary checker took too long: {duration:.2f} seconds"

@pytest.mark.performance
def test_feature_checker_performance(sample_paths, temp_output_dir) -> None:
    """Test feature checker performance with large dataset."""
    # Generate test data
    df = generate_large_dataset()
    
    # Save test file
    data_path = temp_output_dir / "clinical_final.csv"
    df.to_csv(data_path, index=False)
    
    # Update paths
    paths = sample_paths.copy()
    paths["merged_data"] = str(temp_output_dir)
    
    # Measure performance
    start_time = time.time()
    feature_checker.check(
        domain="Clinical",
        input_path="",
        output_path="",
        paths=paths
    )
    duration = time.time() - start_time
    
    # Assert performance criteria
    assert duration < 60, f"Feature checker took too long: {duration:.2f} seconds"