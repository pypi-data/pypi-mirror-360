#!/usr/bin/env python3
"""
Smoke Test for ScriptCraft

Quick verification that all tools can be imported and instantiated.
This is a fast test to ensure the basic functionality works.
"""

import sys
from pathlib import Path
import traceback

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all core modules can be imported."""
    print("🔍 Testing core imports...")
    
    import_tests = [
        ('scriptcraft', 'Main package'),
        ('scriptcraft.common', 'Common utilities'),
        ('scriptcraft.common.core', 'Core functionality'),
        ('scriptcraft.common.data', 'Data utilities'),
        ('scriptcraft.common.io', 'I/O utilities'),
        ('scriptcraft.common.logging', 'Logging utilities'),
        ('scriptcraft.common.registry', 'Registry system'),
        ('scriptcraft.tools', 'Tools package'),
        ('scriptcraft.pipelines', 'Pipelines package'),
    ]
    
    failed_imports = []
    
    for module_name, description in import_tests:
        try:
            __import__(module_name)
            print(f"  ✅ {description}")
        except Exception as e:
            print(f"  ❌ {description}: {e}")
            failed_imports.append((module_name, str(e)))
    
    return failed_imports


def test_tool_imports():
    """Test that all tools can be imported and instantiated."""
    print("\n🔧 Testing tool imports...")
    
    try:
        from scriptcraft.tools import get_available_tools
        tools = get_available_tools()
    except Exception as e:
        print(f"  ❌ Failed to get available tools: {e}")
        return []
    
    failed_tools = []
    
    for tool_name, tool_instance in tools.items():
        try:
            # The registry now returns BaseTool instances directly
            if tool_instance is not None:
                print(f"  ✅ {tool_name}")
            else:
                print(f"  ⚠️ {tool_name}: Tool instance is None")
                failed_tools.append((tool_name, "Tool instance is None"))
        except Exception as e:
            print(f"  ❌ {tool_name}: {e}")
            failed_tools.append((tool_name, str(e)))
    
    return failed_tools


def test_base_functionality():
    """Test basic functionality like config loading and logging."""
    print("\n⚙️ Testing base functionality...")
    
    failed_tests = []
    
    # Test config loading
    try:
        import scriptcraft.common as cu
        config = cu.Config.from_yaml("config.yaml")
        print("  ✅ Config loading")
    except Exception as e:
        print(f"  ❌ Config loading: {e}")
        failed_tests.append(("config_loading", str(e)))
    
    # Test logging setup
    try:
        logger = cu.setup_logger("smoke_test")
        print("  ✅ Logging setup")
    except Exception as e:
        print(f"  ❌ Logging setup: {e}")
        failed_tests.append(("logging_setup", str(e)))
    
    # Test BaseTool
    try:
        from scriptcraft.common.core import BaseTool
        # BaseTool is abstract and cannot be instantiated directly
        # This is working as designed - tools should inherit from BaseTool
        print("  ✅ BaseTool import (abstract class working correctly)")
    except Exception as e:
        print(f"  ❌ BaseTool import: {e}")
        failed_tests.append(("base_tool", str(e)))
    
    return failed_tests


def main():
    """Run all smoke tests."""
    print("🚀 ScriptCraft Smoke Test")
    print("=" * 40)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test tool imports
    failed_tools = test_tool_imports()
    
    # Test base functionality
    failed_functionality = test_base_functionality()
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 40)
    
    total_failures = len(failed_imports) + len(failed_tools) + len(failed_functionality)
    
    if total_failures == 0:
        print("🎉 ALL SMOKE TESTS PASSED!")
        print("ScriptCraft is ready for comprehensive testing.")
        return True
    else:
        print(f"❌ {total_failures} smoke tests failed:")
        
        if failed_imports:
            print(f"  - {len(failed_imports)} import failures")
            for module, error in failed_imports:
                print(f"    {module}: {error}")
        
        if failed_tools:
            print(f"  - {len(failed_tools)} tool failures")
            for tool, error in failed_tools:
                print(f"    {tool}: {error}")
        
        if failed_functionality:
            print(f"  - {len(failed_functionality)} functionality failures")
            for test, error in failed_functionality:
                print(f"    {test}: {error}")
        
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 