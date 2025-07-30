"""
Tests for the tool registry.
"""

import pytest
from pathlib import Path
from scriptcraft.tools.tool_dispatcher import ToolRegistry
from scriptcraft.common.core import BaseTool


class MockTool(BaseTool):
    """A mock tool for testing."""
    
    def __init__(self, name="Mock Tool"):
        super().__init__(name=name, description="A mock tool for testing.")
    
    def run(self, **kwargs):
        """Mock run method."""
        pass


@pytest.fixture
def mock_tool_dir(temp_dir):
    """Create a mock tools directory structure."""
    tools_dir = temp_dir / "tools"
    tools_dir.mkdir()
    
    # Create mock tool directories
    tool1_dir = tools_dir / "tool1"
    tool1_dir.mkdir()
    (tool1_dir / "__init__.py").touch()
    with open(tool1_dir / "main.py", 'w') as f:
        f.write("""
from scriptcraft.common.core import BaseTool

class Tool1(BaseTool):
    def __init__(self):
        super().__init__(name="Tool 1", description="Test Tool 1")
    
    def run(self, **kwargs):
        pass

tool = Tool1()
""")
    
    tool2_dir = tools_dir / "tool2"
    tool2_dir.mkdir()
    (tool2_dir / "__init__.py").touch()
    with open(tool2_dir / "main.py", 'w') as f:
        f.write("""
from scriptcraft.common.core import BaseTool

class Tool2(BaseTool):
    def __init__(self):
        super().__init__(name="Tool 2", description="Test Tool 2")
    
    def run(self, **kwargs):
        pass

tool = Tool2()
""")
    
    return tools_dir


def test_tool_registry_initialization() -> None:
    """Test that registry initializes properly."""
    registry = ToolRegistry()
    assert isinstance(registry._tools, dict)
    assert isinstance(registry._instances, dict)


def test_tool_registry_discover_tools(mock_tool_dir, monkeypatch) -> None:
    """Test tool discovery."""
    monkeypatch.setattr('scriptcraft.tools.tool_dispatcher.TOOLS_FOLDER', mock_tool_dir)
    
    registry = ToolRegistry()
    assert 'tool1' in registry._tools
    assert 'tool2' in registry._tools
    assert registry._tools['tool1'].endswith('.tool1')
    assert registry._tools['tool2'].endswith('.tool2')


def test_tool_registry_get_tool(mock_tool_dir, monkeypatch) -> None:
    """Test getting a tool instance."""
    monkeypatch.setattr('scriptcraft.tools.tool_dispatcher.TOOLS_FOLDER', mock_tool_dir)
    
    registry = ToolRegistry()
    
    # First call should load the tool
    tool1 = registry.get_tool('tool1')
    assert isinstance(tool1, BaseTool)
    assert tool1.name == "Tool 1"
    
    # Second call should return cached instance
    tool1_again = registry.get_tool('tool1')
    assert tool1 is tool1_again  # Same instance
    
    # Non-existent tool should return None
    assert registry.get_tool('nonexistent') is None


def test_tool_registry_list_tools(mock_tool_dir, monkeypatch) -> None:
    """Test listing available tools."""
    monkeypatch.setattr('scriptcraft.tools.tool_dispatcher.TOOLS_FOLDER', mock_tool_dir)
    
    registry = ToolRegistry()
    tools = registry.list_tools()
    
    assert isinstance(tools, dict)
    assert 'tool1' in tools
    assert 'tool2' in tools
    assert tools['tool1'].endswith('.tool1')
    assert tools['tool2'].endswith('.tool2')
    
    # Should be a copy, not the original
    tools['new'] = 'test'
    assert 'new' not in registry._tools


def test_tool_registry_caching(mock_tool_dir, monkeypatch) -> None:
    """Test that tools are properly cached."""
    monkeypatch.setattr('scriptcraft.tools.tool_dispatcher.TOOLS_FOLDER', mock_tool_dir)
    
    registry = ToolRegistry()
    
    # First call loads the tool
    tool1_first = registry.get_tool('tool1')
    assert tool1_first is not None
    
    # Modify the cached instance
    tool1_first.description = "Modified description"
    
    # Second call should return the modified instance
    tool1_second = registry.get_tool('tool1')
    assert tool1_second.description == "Modified description"
    assert tool1_first is tool1_second 