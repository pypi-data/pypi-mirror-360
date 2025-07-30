"""
Tests for the RHQ Form Autofiller tool.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from selenium.webdriver.common.by import By

from scriptcraft.tools.rhq_form_autofiller.main import RHQFormAutofiller


@pytest.fixture
def mock_webdriver():
    """Create a mock Selenium webdriver."""
    driver = MagicMock()
    
    # Mock find_element to return a mock element
    def mock_find_element(by, value):
        element = MagicMock()
        element.text = f"Mock element {value}"
        return element
    
    driver.find_element = mock_find_element
    return driver


@pytest.fixture
def mock_chrome_options():
    """Create mock Chrome options."""
    options = MagicMock()
    return options


@pytest.fixture
def tool():
    """Create an instance of the RHQ Form Autofiller tool."""
    return RHQFormAutofiller()


def test_tool_initialization(tool) -> None:
    """Test tool initialization."""
    assert tool.name == "RHQ Form Autofiller"
    assert "RHQ forms" in tool.description.lower()
    assert tool.driver is None


@patch('scripts.tools.rhq_form_autofiller.utils.webdriver.Chrome')
def test_tool_run_with_valid_input(mock_chrome, tool, sample_excel_file, temp_dir, mock_webdriver) -> None:
    """Test running the tool with valid input."""
    # Setup mock Chrome driver
    mock_chrome.return_value = mock_webdriver
    
    # Run the tool
    tool.run(
        input_paths=[sample_excel_file],
        output_dir=temp_dir
    )
    
    # Verify Chrome was initialized
    mock_chrome.assert_called_once()
    
    # Verify driver was quit
    assert mock_webdriver.quit.called


def test_tool_run_without_input(tool) -> None:
    """Test running the tool without input."""
    with pytest.raises(ValueError) as exc:
        tool.run()
    assert "No input Excel file provided" in str(exc.value)


def test_tool_run_with_nonexistent_file(tool, temp_dir) -> None:
    """Test running the tool with a non-existent file."""
    with pytest.raises(FileNotFoundError):
        tool.run(
            input_paths=[temp_dir / "nonexistent.xlsx"],
            output_dir=temp_dir
        )


@patch('scripts.tools.rhq_form_autofiller.utils.webdriver.Chrome')
def test_tool_cleanup_on_error(mock_chrome, tool, sample_excel_file, temp_dir, mock_webdriver) -> None:
    """Test that the tool cleans up resources on error."""
    # Setup mock Chrome driver to raise an exception
    mock_chrome.return_value = mock_webdriver
    mock_webdriver.find_element.side_effect = Exception("Test error")
    
    # Run the tool and expect an exception
    with pytest.raises(Exception):
        tool.run(
            input_paths=[sample_excel_file],
            output_dir=temp_dir
        )
    
    # Verify driver was quit even after error
    assert mock_webdriver.quit.called


@patch('scripts.tools.rhq_form_autofiller.utils.webdriver.Chrome')
def test_tool_med_id_filtering(mock_chrome, tool, sample_excel_file, temp_dir, mock_webdriver) -> None:
    """Test that the tool correctly filters by Med ID."""
    # Setup mock Chrome driver
    mock_chrome.return_value = mock_webdriver
    
    # Run the tool with Med ID filter
    tool.run(
        input_paths=[sample_excel_file],
        output_dir=temp_dir,
        med_id="M001"
    )
    
    # Verify Chrome was initialized
    mock_chrome.assert_called_once()
    
    # Verify driver interactions
    # Note: This is a basic test, you might want to add more specific assertions
    # based on your actual implementation
    assert mock_webdriver.find_element.called 