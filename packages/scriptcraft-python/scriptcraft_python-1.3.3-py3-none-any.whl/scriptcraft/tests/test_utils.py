"""
Test utilities for ScriptCraft.

This module provides DRY, scalable testing patterns and utilities for all ScriptCraft components.
Use these utilities to ensure consistent, maintainable tests across the codebase.
"""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Union, Optional, Generator, Any
from unittest.mock import Mock, patch, MagicMock
import logging

# Import ScriptCraft utilities
import scriptcraft.common as cu


class TestDataManager:
    """Manages test data creation and cleanup."""
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.created_files: List[Path] = []
        self.created_dirs: List[Path] = []
    
    def create_sample_dataframe(self, 
                               rows: int = 10, 
                               columns: Optional[Dict[str, List[Any]]] = None,
                               filename: str = "sample_data.csv") -> Path:
        """Create a sample DataFrame for testing."""
        if columns is None:
            columns = {
                'Research ID': [f'R{i:03d}' for i in range(1, rows + 1)],
                'Med ID': [f'M{i:03d}' for i in range(1, rows + 1)],
                'Visit': [f'V{i}' for i in range(1, rows + 1)],
                'Age': [20 + i for i in range(rows)],
                'Score': [50 + i * 2 for i in range(rows)],
                'Date': [f'2020-{i+1:02d}-01' for i in range(rows)]
            }
        
        df = pd.DataFrame(columns)
        file_path = self.temp_dir / filename
        df.to_csv(file_path, index=False)
        self.created_files.append(file_path)
        return file_path
    
    def create_sample_excel(self, 
                           rows: int = 10,
                           filename: str = "sample_data.xlsx") -> Path:
        """Create a sample Excel file for testing."""
        df = self.create_sample_dataframe(rows)
        excel_path = self.temp_dir / filename
        df.to_excel(excel_path, index=False)
        self.created_files.append(excel_path)
        return excel_path
    
    def create_sample_dictionary(self, 
                                columns: Optional[List[str]] = None,
                                filename: str = "sample_dictionary.csv") -> Path:
        """Create a sample data dictionary for testing."""
        if columns is None:
            columns = ['Variable', 'Type', 'Description', 'Values', 'Required']
        
        data = {
            'Variable': ['Research ID', 'Med ID', 'Visit', 'Age', 'Score'],
            'Type': ['string', 'string', 'string', 'integer', 'float'],
            'Description': ['Research identifier', 'Medical identifier', 'Visit number', 'Age in years', 'Test score'],
            'Values': ['R001-R999', 'M001-M999', 'V1-V10', '0-120', '0-100'],
            'Required': ['Yes', 'Yes', 'Yes', 'No', 'No']
        }
        
        df = pd.DataFrame(data)
        file_path = self.temp_dir / filename
        df.to_csv(file_path, index=False)
        self.created_files.append(file_path)
        return file_path
    
    def create_domain_structure(self, domain: str = "test_domain") -> Dict[str, Path]:
        """Create a complete domain directory structure for testing."""
        domain_dir = self.temp_dir / domain
        domain_dir.mkdir(exist_ok=True)
        
        structure = {
            'raw_data': domain_dir / 'raw_data',
            'processed_data': domain_dir / 'processed_data',
            'qc_logs': domain_dir / 'qc_logs',
            'qc_output': domain_dir / 'qc_output'
        }
        
        for path in structure.values():
            path.mkdir(exist_ok=True)
            self.created_dirs.append(path)
        
        return structure
    
    def cleanup(self):
        """Clean up all created files and directories."""
        for file_path in self.created_files:
            if file_path.exists():
                file_path.unlink()
        
        for dir_path in reversed(self.created_dirs):
            if dir_path.exists():
                shutil.rmtree(dir_path)


class ToolTestHelper:
    """Helper class for testing ScriptCraft tools."""
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.data_manager = TestDataManager(temp_dir)
    
    def create_tool_test_environment(self, 
                                   tool_name: str,
                                   domain: str = "test_domain") -> Dict[str, Any]:
        """Create a complete test environment for a tool."""
        # Create domain structure
        domain_paths = self.data_manager.create_domain_structure(domain)
        
        # Create sample data files
        input_file = self.data_manager.create_sample_dataframe(
            filename=f"{domain}_data.csv"
        )
        
        # Create output directory
        output_dir = self.temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Create mock config
        config = Mock()
        config.get_domain_paths.return_value = domain_paths
        config.get_logging_config.return_value = Mock()
        
        return {
            'input_file': input_file,
            'output_dir': output_dir,
            'domain': domain,
            'domain_paths': domain_paths,
            'config': config,
            'temp_dir': self.temp_dir
        }
    
    def run_tool_test(self, 
                     tool_class,
                     input_paths: Optional[List[Path]] = None,
                     output_dir: Optional[Path] = None,
                     domain: Optional[str] = None,
                     **kwargs) -> Dict[str, Any]:
        """Run a tool test with standard setup and teardown."""
        if input_paths is None:
            input_paths = [self.data_manager.create_sample_dataframe()]
        
        if output_dir is None:
            output_dir = self.temp_dir / "output"
            output_dir.mkdir(exist_ok=True)
        
        # Create tool instance
        tool = tool_class()
        
        # Run tool
        try:
            result = tool.run(
                input_paths=input_paths,
                output_dir=output_dir,
                domain=domain,
                **kwargs
            )
            
            return {
                'success': True,
                'result': result,
                'tool': tool,
                'input_paths': input_paths,
                'output_dir': output_dir,
                'domain': domain
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': e,
                'tool': tool,
                'input_paths': input_paths,
                'output_dir': output_dir,
                'domain': domain
            }
    
    def cleanup(self):
        """Clean up test environment."""
        self.data_manager.cleanup()


class MockConfig:
    """Mock configuration for testing."""
    
    def __init__(self, **kwargs):
        self._data = {
            'workspace_root': Path.cwd(),
            'domains': ['Biomarkers', 'Clinical', 'Genomics', 'Imaging'],
            'logging': {
                'level': 'INFO',
                'log_dir': 'logs',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'tools': {},
            **kwargs
        }
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        keys = key.split('.')
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_domain_paths(self, domain: str) -> Dict[str, Path]:
        """Get domain paths."""
        base_path = Path.cwd() / "domains" / domain
        return {
            'raw_data': base_path / 'raw_data',
            'processed_data': base_path / 'processed_data',
            'qc_logs': base_path / 'qc_logs',
            'qc_output': base_path / 'qc_output'
        }
    
    def get_logging_config(self):
        """Get logging configuration."""
        return self._data['logging']


# ===== PYTEST FIXTURES =====

@pytest.fixture
def test_data_manager(tmp_path) -> Generator[TestDataManager, None, None]:
    """Provide a test data manager."""
    manager = TestDataManager(tmp_path)
    yield manager
    manager.cleanup()


@pytest.fixture
def tool_test_helper(tmp_path) -> Generator[ToolTestHelper, None, None]:
    """Provide a tool test helper."""
    helper = ToolTestHelper(tmp_path)
    yield helper
    helper.cleanup()


@pytest.fixture
def mock_config() -> MockConfig:
    """Provide a mock configuration."""
    return MockConfig()


@pytest.fixture
def sample_dataframe(test_data_manager) -> pd.DataFrame:
    """Provide a sample DataFrame."""
    file_path = test_data_manager.create_sample_dataframe()
    return pd.read_csv(file_path)


@pytest.fixture
def sample_excel_file(test_data_manager) -> Path:
    """Provide a sample Excel file."""
    return test_data_manager.create_sample_excel()


@pytest.fixture
def sample_dictionary(test_data_manager) -> Path:
    """Provide a sample data dictionary."""
    return test_data_manager.create_sample_dictionary()


@pytest.fixture
def domain_structure(test_data_manager) -> Dict[str, Path]:
    """Provide a complete domain directory structure."""
    return test_data_manager.create_domain_structure()


# ===== TEST DECORATORS =====

def smoke_test(func):
    """Decorator for smoke tests."""
    return pytest.mark.smoke(func)


def integration_test(func):
    """Decorator for integration tests."""
    return pytest.mark.integration(func)


def system_test(func):
    """Decorator for system tests."""
    return pytest.mark.system(func)


def performance_test(func):
    """Decorator for performance tests."""
    return pytest.mark.performance(func)


def slow_test(func):
    """Decorator for slow tests."""
    return pytest.mark.slow(func)


# ===== ASSERTION HELPERS =====

def assert_file_exists(file_path: Path, description: str = "File"):
    """Assert that a file exists."""
    assert file_path.exists(), f"{description} should exist: {file_path}"


def assert_file_not_empty(file_path: Path, description: str = "File"):
    """Assert that a file exists and is not empty."""
    assert_file_exists(file_path, description)
    assert file_path.stat().st_size > 0, f"{description} should not be empty: {file_path}"


def assert_dataframe_not_empty(df: pd.DataFrame, description: str = "DataFrame"):
    """Assert that a DataFrame is not empty."""
    assert not df.empty, f"{description} should not be empty"


def assert_dataframe_has_columns(df: pd.DataFrame, expected_columns: List[str], description: str = "DataFrame"):
    """Assert that a DataFrame has the expected columns."""
    missing_columns = set(expected_columns) - set(df.columns)
    assert not missing_columns, f"{description} missing columns: {missing_columns}"


def assert_log_contains(caplog, expected_message: str, level: str = "INFO"):
    """Assert that a log message was recorded."""
    log_messages = [record.message for record in caplog.records if record.levelname == level]
    assert any(expected_message in msg for msg in log_messages), f"Expected log message not found: {expected_message}"


# ===== UTILITY FUNCTIONS =====

def create_temp_file(content: str = "", suffix: str = ".txt") -> Path:
    """Create a temporary file with content."""
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_file.write(content.encode())
    temp_file.close()
    return Path(temp_file.name)


def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame, ignore_index: bool = True) -> bool:
    """Compare two DataFrames for equality."""
    if ignore_index:
        df1 = df1.reset_index(drop=True)
        df2 = df2.reset_index(drop=True)
    return df1.equals(df2)


def setup_test_logging(level: str = "INFO") -> None:
    """Setup logging for tests."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def cleanup_temp_files(*file_paths: Path) -> None:
    """Clean up temporary files."""
    for file_path in file_paths:
        if file_path.exists():
            file_path.unlink() 