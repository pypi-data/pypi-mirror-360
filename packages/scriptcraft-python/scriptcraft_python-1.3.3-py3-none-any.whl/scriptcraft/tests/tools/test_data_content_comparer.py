"""
Tests for the Data Content Comparer tool.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from scripts.tools.data_content_comparer.main import DataContentComparer


@pytest.fixture
def tool():
    """Create an instance of the Data Content Comparer tool."""
    return DataContentComparer()


def test_tool_initialization(tool) -> None:
    """Test tool initialization."""
    assert tool.name == "Data Content Comparer"
    assert "compar" in tool.description.lower()


def test_tool_run_without_mode(tool, sample_comparison_files) -> None:
    """Test running the tool without a mode."""
    with pytest.raises(ValueError) as exc:
        tool.run(input_paths=list(sample_comparison_files))
    assert "Comparison mode is required" in str(exc.value)


def test_tool_run_with_invalid_mode(tool, sample_comparison_files) -> None:
    """Test running the tool with an invalid mode."""
    with pytest.raises(ValueError) as exc:
        tool.run(
            mode="invalid_mode",
            input_paths=list(sample_comparison_files)
        )
    assert "Invalid mode" in str(exc.value)


def test_tool_run_without_input_files(tool) -> None:
    """Test running the tool without input files."""
    with pytest.raises(ValueError) as exc:
        tool.run(mode="standard")
    assert "No input files provided" in str(exc.value)


@patch('scripts.tools.data_content_comparer.utils.load_mode')
def test_tool_run_with_valid_input(mock_load_mode, tool, sample_comparison_files, temp_dir) -> None:
    """Test running the tool with valid input."""
    # Create mock mode function
    mock_mode_func = MagicMock()
    mock_load_mode.return_value = mock_mode_func
    
    # Run the tool
    tool.run(
        mode="standard",
        input_paths=list(sample_comparison_files),
        output_dir=temp_dir
    )
    
    # Verify mode was loaded and called
    mock_load_mode.assert_called_once_with("standard")
    mock_mode_func.assert_called_once()
    
    # Verify mode function was called with correct arguments
    call_args = mock_mode_func.call_args[1]
    assert "input_paths" in call_args
    assert "output_dir" in call_args
    assert len(call_args["input_paths"]) == 2


@patch('scripts.tools.data_content_comparer.utils.load_mode')
def test_tool_standard_mode_comparison(mock_load_mode, tool, temp_dir) -> None:
    """Test standard mode comparison with specific content."""
    # Create test files with known differences
    file1 = temp_dir / "file1.txt"
    file2 = temp_dir / "file2.txt"
    
    with open(file1, 'w') as f:
        f.write("Line 1\nLine 2\nLine 3\n")
    with open(file2, 'w') as f:
        f.write("Line 1\nModified Line 2\nLine 3\n")
    
    # Create mock mode function that implements simple comparison
    def mock_compare(input_paths, output_dir, **kwargs):
        with open(output_dir / "comparison.txt", 'w') as f:
            f.write("Found differences in line 2")
    
    mock_mode_func = MagicMock(side_effect=mock_compare)
    mock_load_mode.return_value = mock_mode_func
    
    # Run the tool
    tool.run(
        mode="standard",
        input_paths=[file1, file2],
        output_dir=temp_dir
    )
    
    # Verify comparison output was created
    output_file = temp_dir / "comparison.txt"
    assert output_file.exists()
    assert "differences in line 2" in output_file.read_text()


@patch('scripts.tools.data_content_comparer.utils.load_mode')
def test_tool_rhq_mode_comparison(mock_load_mode, tool, sample_excel_file, temp_dir) -> None:
    """Test RHQ mode comparison with Excel files."""
    # Create a second Excel file with modifications
    import pandas as pd
    df = pd.read_excel(sample_excel_file)
    df.loc[0, 'Med ID'] = 'MODIFIED'
    modified_excel = temp_dir / "modified.xlsx"
    df.to_excel(modified_excel)
    
    # Create mock mode function that implements RHQ comparison
    def mock_compare(input_paths, output_dir, **kwargs):
        with open(output_dir / "rhq_comparison.txt", 'w') as f:
            f.write("Found differences in Med ID")
    
    mock_mode_func = MagicMock(side_effect=mock_compare)
    mock_load_mode.return_value = mock_mode_func
    
    # Run the tool
    tool.run(
        mode="rhq_mode",
        input_paths=[sample_excel_file, modified_excel],
        output_dir=temp_dir
    )
    
    # Verify comparison output was created
    output_file = temp_dir / "rhq_comparison.txt"
    assert output_file.exists()
    assert "differences in Med ID" in output_file.read_text()


def test_tool_output_directory_creation(tool, sample_comparison_files) -> None:
    """Test that the tool creates output directory if it doesn't exist."""
    output_dir = Path("nonexistent_dir")
    
    @patch('scripts.tools.data_content_comparer.utils.load_mode')
    def run_test(mock_load_mode):
        mock_mode_func = MagicMock()
        mock_load_mode.return_value = mock_mode_func
        
        tool.run(
            mode="standard",
            input_paths=list(sample_comparison_files),
            output_dir=output_dir
        )
        
        assert output_dir.exists()
        assert output_dir.is_dir()
        
        # Cleanup
        output_dir.rmdir()
    
    run_test()


@patch('scripts.tools.data_content_comparer.utils.load_mode')
def test_tool_domain_handling(mock_load_mode, tool, sample_comparison_files, temp_dir) -> None:
    """Test that the tool correctly handles domain parameter."""
    mock_mode_func = MagicMock()
    mock_load_mode.return_value = mock_mode_func
    
    test_domain = "test_domain"
    
    tool.run(
        mode="standard",
        input_paths=list(sample_comparison_files),
        output_dir=temp_dir,
        domain=test_domain
    )
    
    # Verify domain was passed to mode function
    call_kwargs = mock_mode_func.call_args[1]
    assert call_kwargs.get("domain") == test_domain 