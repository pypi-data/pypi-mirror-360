"""Tests for the Base Enhancement class."""

import pytest
from pathlib import Path
import pandas as pd

from scriptcraft.common.core import BaseTool


class DummyEnhancement(BaseTool):
    """Dummy enhancement class for testing."""
    
    def __init__(self):
        super().__init__(
            name="Dummy Enhancement",
            description="A dummy enhancement for testing."
        )
    
    def run(self, input_data, **kwargs):
        """Dummy run method that adds a test column."""
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")
        
        if isinstance(input_data, pd.DataFrame):
            result = input_data.copy()
            result['test'] = 'dummy'
            return result
        else:
            return {k: self.run(v) for k, v in input_data.items()}


def test_base_enhancement_initialization() -> None:
    """Test base enhancement initialization."""
    enhancement = DummyEnhancement()
    assert enhancement.name == "Dummy Enhancement"
    assert enhancement.description == "A dummy enhancement for testing."


def test_base_enhancement_validate_input() -> None:
    """Test input validation."""
    enhancement = DummyEnhancement()
    
    # Test with valid DataFrame
    valid_df = pd.DataFrame({'col': [1, 2, 3]})
    assert enhancement.validate_input(valid_df) is True
    
    # Test with empty DataFrame
    empty_df = pd.DataFrame()
    assert enhancement.validate_input(empty_df) is False
    
    # Test with valid dict of DataFrames
    valid_dict = {
        'df1': pd.DataFrame({'col': [1, 2]}),
        'df2': pd.DataFrame({'col': [3, 4]})
    }
    assert enhancement.validate_input(valid_dict) is True
    
    # Test with dict containing empty DataFrame
    invalid_dict = {
        'df1': pd.DataFrame({'col': [1, 2]}),
        'df2': pd.DataFrame()
    }
    assert enhancement.validate_input(invalid_dict) is False
    
    # Test with invalid input type
    assert enhancement.validate_input([1, 2, 3]) is False


def test_base_enhancement_save_output(tmp_path) -> None:
    """Test output saving functionality."""
    enhancement = DummyEnhancement()
    test_df = pd.DataFrame({'col': [1, 2, 3]})
    
    # Test saving as Excel
    excel_path = tmp_path / "test.xlsx"
    enhancement.save_output(test_df, excel_path)
    assert excel_path.exists()
    saved_excel = pd.read_excel(excel_path)
    pd.testing.assert_frame_equal(saved_excel, test_df)
    
    # Test saving as CSV
    csv_path = tmp_path / "test.csv"
    enhancement.save_output(test_df, csv_path)
    assert csv_path.exists()
    saved_csv = pd.read_csv(csv_path)
    pd.testing.assert_frame_equal(saved_csv, test_df)


def test_base_enhancement_logging(caplog) -> None:
    """Test logging functionality."""
    enhancement = DummyEnhancement()
    
    # Test normal logging
    enhancement.log_and_print("Test message")
    assert "[Dummy Enhancement] Test message" in caplog.text
    
    # Test start logging
    enhancement.log_start()
    assert "[Dummy Enhancement] 🚀 Starting Dummy Enhancement..." in caplog.text
    
    # Test completion logging
    enhancement.log_completion()
    assert "[Dummy Enhancement] ✅ Dummy Enhancement completed successfully" in caplog.text
    
    # Test completion logging with output path
    output_path = Path("test/path.xlsx")
    enhancement.log_completion(output_path)
    assert f"[Dummy Enhancement] ✅ Dummy Enhancement completed successfully\n📄 Output saved to: {output_path}" in caplog.text


def test_base_enhancement_enhance() -> None:
    """Test enhance functionality with dummy enhancement."""
    enhancement = DummyEnhancement()
    
    # Test with single DataFrame
    input_df = pd.DataFrame({'col': [1, 2, 3]})
    result = enhancement.run(input_df)
    assert isinstance(result, pd.DataFrame)
    assert 'test' in result.columns
    assert all(result['test'] == 'dummy')
    
    # Test with dict of DataFrames
    input_dict = {
        'df1': pd.DataFrame({'col': [1, 2]}),
        'df2': pd.DataFrame({'col': [3, 4]})
    }
    result_dict = enhancement.run(input_dict)
    assert isinstance(result_dict, dict)
    assert all('test' in df.columns for df in result_dict.values())
    assert all(all(df['test'] == 'dummy') for df in result_dict.values())
    
    # Test with invalid input
    with pytest.raises(ValueError):
        enhancement.run(pd.DataFrame()) 