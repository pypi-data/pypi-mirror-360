"""Tests for the Supplement Prepper enhancement."""

import pytest
from pathlib import Path
import pandas as pd

from scripts.enhancements.supplement_prepper.main import enhancement as prepper
from scriptcraft.common import load_data


def test_supplement_prepper_initialization() -> None:
    """Test supplement prepper initialization."""
    assert prepper.name == "Supplement Prepper"
    assert isinstance(prepper.root, Path)
    assert isinstance(prepper.default_input_files, list)
    assert isinstance(prepper.default_output_path, Path)


def test_supplement_prepper_with_input_data(tmp_path) -> None:
    """Test supplement prepper with pre-loaded input data."""
    # Create test data
    df1 = pd.DataFrame({
        'ID': [1, 2],
        'Value': ['A', 'B']
    })
    df2 = pd.DataFrame({
        'ID': [3, 4],
        'Value': ['C', 'D']
    })
    
    # Save test files
    input_files = []
    for i, df in enumerate([df1, df2]):
        path = tmp_path / f"test_supplement_{i}.xlsx"
        df.to_excel(path, index=False)
        input_files.append(path)
    
    output_path = tmp_path / "merged_supplement.xlsx"
    
    # Run enhancement
    result = prepper.enhance(
        kwargs={
            'input_files': input_files,
            'output_path': output_path
        }
    )
    
    # Verify results
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4  # Combined length of both dataframes
    assert output_path.exists()
    
    # Load and verify output file
    output_df = load_data(output_path)
    pd.testing.assert_frame_equal(output_df, result)


def test_supplement_prepper_missing_files() -> None:
    """Test supplement prepper with missing input files."""
    with pytest.raises(FileNotFoundError):
        prepper.enhance(
            kwargs={
                'input_files': [Path('nonexistent1.xlsx'), Path('nonexistent2.xlsx')]
            }
        )


def test_supplement_prepper_empty_files(tmp_path) -> None:
    """Test supplement prepper with empty input files."""
    # Create empty test files
    empty_df1 = pd.DataFrame()
    empty_df2 = pd.DataFrame()
    
    input_files = []
    for i, df in enumerate([empty_df1, empty_df2]):
        path = tmp_path / f"empty_supplement_{i}.xlsx"
        df.to_excel(path, index=False)
        input_files.append(path)
    
    output_path = tmp_path / "merged_empty.xlsx"
    
    # Run enhancement and verify it handles empty files appropriately
    result = prepper.enhance(
        kwargs={
            'input_files': input_files,
            'output_path': output_path
        }
    )
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0  # Should be empty 