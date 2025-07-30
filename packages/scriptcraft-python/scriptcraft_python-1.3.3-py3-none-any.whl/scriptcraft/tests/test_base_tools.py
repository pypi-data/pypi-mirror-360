"""
Tests for the base tools framework.
"""

import pytest
from pathlib import Path
from typing import Optional, List, Union

from scriptcraft.common.core import BaseTool


class DummyTool(BaseTool):
    """A dummy tool for testing."""
    
    def __init__(self):
        super().__init__(
            name="Dummy Tool",
            description="A dummy tool for testing."
        )
        self.run_called = False
        self.last_args = None
    
    def run(self,
            mode: Optional[str] = None,
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs) -> None:
        """Record that run was called with these args."""
        self.run_called = True
        self.last_args = {
            'mode': mode,
            'input_paths': input_paths,
            'output_dir': output_dir,
            'domain': domain,
            'output_filename': output_filename,
            'kwargs': kwargs
        }


def test_base_tool_initialization() -> None:
    """Test that a tool can be properly initialized."""
    tool = DummyTool()
    assert tool.name == "Dummy Tool"
    assert tool.description == "A dummy tool for testing."
    assert not tool.run_called


def test_base_tool_run_records_args() -> None:
    """Test that run method properly records arguments."""
    tool = DummyTool()
    test_args = {
        'mode': 'test_mode',
        'input_paths': ['test.txt'],
        'output_dir': 'output',
        'domain': 'test_domain',
        'output_filename': 'output.txt',
        'extra_arg': 'value'
    }
    
    tool.run(**test_args)
    assert tool.run_called
    assert tool.last_args['mode'] == test_args['mode']
    assert tool.last_args['input_paths'] == test_args['input_paths']
    assert tool.last_args['output_dir'] == test_args['output_dir']
    assert tool.last_args['domain'] == test_args['domain']
    assert tool.last_args['output_filename'] == test_args['output_filename']
    assert tool.last_args['kwargs']['extra_arg'] == test_args['extra_arg']


def test_base_tool_validate_inputs(temp_dir) -> None:
    """Test input validation."""
    tool = DummyTool()
    
    # Test with no inputs
    assert not tool.validate_inputs([])
    
    # Test with non-existent file
    assert not tool.validate_inputs([temp_dir / "nonexistent.txt"])
    
    # Test with existing file
    test_file = temp_dir / "test.txt"
    test_file.touch()
    assert tool.validate_inputs([test_file])


def test_base_tool_ensure_output_dir(temp_dir) -> None:
    """Test output directory creation."""
    tool = DummyTool()
    
    # Test creating new directory
    new_dir = temp_dir / "new_output_dir"
    created_dir = tool.ensure_output_dir(new_dir)
    assert created_dir.exists()
    assert created_dir.is_dir()
    
    # Test with existing directory
    existing_dir = temp_dir / "existing_dir"
    existing_dir.mkdir()
    created_dir = tool.ensure_output_dir(existing_dir)
    assert created_dir.exists()
    assert created_dir.is_dir()


def test_base_tool_logging(caplog) -> None:
    """Test logging functionality."""
    tool = DummyTool()
    
    # Test start logging
    tool.log_start()
    assert "Starting Dummy Tool..." in caplog.text
    
    # Test completion logging
    output_path = Path("test_output.txt")
    tool.log_completion(output_path)
    assert "Dummy Tool completed successfully" in caplog.text
    assert str(output_path) in caplog.text
    
    # Test completion without output path
    caplog.clear()
    tool.log_completion()
    assert "Dummy Tool completed successfully" in caplog.text 