"""
Tests for the unified plugin system.

This module tests plugin registration, discovery, and loading functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from scriptcraft.common.plugins import (
    registry, 
    PluginBase, 
    UnifiedPluginRegistry,
    register_validator,
    register_tool,
    register_pipeline_step
)
from scriptcraft.common.data.validation import ColumnValidator


class TestPluginBase:
    """Test the PluginBase class."""
    
    def test_plugin_base_initialization(self) -> None:
        """Test that PluginBase can be initialized."""
        class TestPlugin(PluginBase):
            def get_plugin_type(self):
                return 'test'
        
        plugin = TestPlugin()
        assert plugin.name == 'TestPlugin'
        assert plugin.description == 'Test plugin for testing.'


class TestValidatorPlugin:
    """Test validator plugin registration and functionality."""
    
    def test_validator_plugin_registration(self) -> None:
        """Test that validator plugins can be registered."""
        @register_validator('test_validator')
        class TestValidator(ColumnValidator):
            """Test validator for testing."""
            def validate_value(self, value, expected_values):
                return None  # Always valid for testing
        
        # Check that the plugin was registered
        validators = registry.get_all_plugins('validator')
        assert 'test_validator' in validators
        assert validators['test_validator'] == TestValidator
    
    def test_validator_plugin_metadata(self) -> None:
        """Test that validator plugin metadata is stored correctly."""
        @register_validator('test_metadata', version='1.0.0')
        class TestValidator(ColumnValidator):
            """Test validator with metadata."""
            def validate_value(self, value, expected_values):
                return None
        
        metadata = registry.get_metadata('validator', 'test_metadata')
        assert metadata['version'] == '1.0.0'


class TestToolPlugin:
    """Test tool plugin registration and functionality."""
    
    def test_tool_plugin_registration(self) -> None:
        """Test that tool plugins can be registered."""
        class MockTool:
            def run(self):
                return True
        
        @register_tool('test_tool', description='Test tool')
        class TestToolPlugin(MockTool, PluginBase):
            def get_plugin_type(self):
                return 'tool'
        
        # Check that the plugin was registered
        tools = registry.get_all_plugins('tool')
        assert 'test_tool' in tools
        assert tools['test_tool'] == TestToolPlugin
    
    def test_tool_plugin_metadata(self) -> None:
        """Test that tool plugin metadata is stored correctly."""
        class MockTool:
            def run(self):
                return True
        
        @register_tool('test_tool_metadata', description='Test tool with metadata', version='2.0.0')
        class TestToolPlugin(MockTool, PluginBase):
            def get_plugin_type(self):
                return 'tool'
        
        metadata = registry.get_metadata('tool', 'test_tool_metadata')
        assert metadata['description'] == 'Test tool with metadata'
        assert metadata['version'] == '2.0.0'


class TestPipelineStepPlugin:
    """Test pipeline step plugin registration and functionality."""
    
    def test_pipeline_step_plugin_registration(self) -> None:
        """Test that pipeline step plugins can be registered."""
        @register_pipeline_step('test_step')
        def test_pipeline_step() -> None:
            return True
        
        # Check that the plugin was registered
        steps = registry.get_all_plugins('pipeline_step')
        assert 'test_step' in steps
        assert steps['test_step'] == test_pipeline_step


class TestPluginRegistry:
    """Test the UnifiedPluginRegistry functionality."""
    
    def test_registry_initialization(self) -> None:
        """Test that the registry initializes correctly."""
        test_registry = UnifiedPluginRegistry()
        assert test_registry._plugins == {}
        assert test_registry._metadata == {}
        assert test_registry._loaders == {}
    
    def test_plugin_listing(self) -> None:
        """Test that plugins can be listed by type."""
        # Register a test validator
        @register_validator('test_listing')
        class TestValidator(ColumnValidator):
            def validate_value(self, value, expected_values):
                return None
        
        # List all validator plugins
        validator_plugins = registry.list_plugins('validator')
        assert 'test_listing' in validator_plugins
        
        # List all plugins
        all_plugins = registry.list_plugins()
        assert 'test_listing' in all_plugins
    
    def test_plugin_instance_creation(self) -> None:
        """Test that plugin instances can be created."""
        @register_validator('test_instance')
        class TestValidator(ColumnValidator):
            def validate_value(self, value, expected_values):
                return None
        
        # Create an instance
        instance = registry.get_plugin_instance('validator', 'test_instance')
        assert isinstance(instance, TestValidator)
        assert instance.get_plugin_type() == 'validator'
    
    def test_nonexistent_plugin(self) -> None:
        """Test handling of nonexistent plugins."""
        # Try to get a plugin that doesn't exist
        plugin = registry.get_plugin('validator', 'nonexistent')
        assert plugin is None
        
        # Try to get an instance of a nonexistent plugin
        instance = registry.get_plugin_instance('validator', 'nonexistent')
        assert instance is None


class TestPluginDiscovery:
    """Test plugin discovery and loading functionality."""
    
    def test_plugin_discovery_structure(self) -> None:
        """Test that the plugin discovery structure is correct."""
        # The registry should look for plugins in these directories:
        # - plugins/validators/
        # - plugins/tools/
        # - plugins/pipeline/
        
        # This is a structural test - actual discovery would require
        # creating test directories and modules
        assert hasattr(registry, 'discover_plugins')
        assert hasattr(registry, 'load_plugins_from_directory')
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_plugin_discovery_mock(self, mock_glob, mock_exists) -> None:
        """Test plugin discovery with mocked file system."""
        # Mock that directories exist
        mock_exists.return_value = True
        
        # Mock that no Python files are found
        mock_glob.return_value = []
        
        # This should not raise an exception
        test_path = Path('/test/path')
        registry.discover_plugins(test_path)


class TestBackwardCompatibility:
    """Test backward compatibility with legacy plugin systems."""
    
    def test_legacy_plugin_registry_compatibility(self) -> None:
        """Test that legacy PluginRegistry still works."""
        from scriptcraft.common.data.validation import PluginRegistry
        
        legacy_registry = PluginRegistry()
        
        @legacy_registry.register('legacy_test')
        class LegacyValidator(ColumnValidator):
            def validate_value(self, value, expected_values):
                return None
        
        # Check that it's registered in the legacy registry
        validators = legacy_registry.get_all_validators()
        assert 'legacy_test' in validators
        
        # Check that it's also registered in the unified registry
        unified_validators = registry.get_all_plugins('validator')
        assert 'legacy_test' in unified_validators


# Test fixtures for cleanup
@pytest.fixture(autouse=True)
def cleanup_registry():
    """Clean up the registry after each test."""
    yield
    # Clear the registry after each test
    registry._plugins.clear()
    registry._metadata.clear()


if __name__ == '__main__':
    # Basic test runner for development
    print("Running plugin system tests...")
    
    # Test basic functionality
    test_registry = TestPluginRegistry()
    test_registry.test_registry_initialization()
    test_registry.test_plugin_listing()
    
    print("✅ Basic plugin system tests passed!") 