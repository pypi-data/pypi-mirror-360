"""
Test for ScriptCraft Unified Registry System
"""

def test_registry_and_tool_discovery() -> None:
    import scriptcraft.common as cu
    # Registry should be available
    assert hasattr(cu, 'registry')
    # get_available_tools should be available
    assert hasattr(cu, 'get_available_tools')
    # Should return at least the exemplar tool
    tools = cu.get_available_tools()
    assert isinstance(tools, dict)
    assert 'rhq_form_autofiller' in tools or len(tools) > 0 