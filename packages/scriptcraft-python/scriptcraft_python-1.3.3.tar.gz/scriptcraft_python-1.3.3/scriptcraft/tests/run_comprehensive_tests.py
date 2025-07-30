#!/usr/bin/env python3
"""
Comprehensive Test Runner for ScriptCraft

This script runs all tests systematically to ensure the entire ScriptCraft codebase
works correctly after standardization and DRY improvements.

Usage:
    python run_comprehensive_tests.py [--category CATEGORY] [--tool TOOL_NAME] [--verbose]
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import time
import json

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import scriptcraft.common as cu


class TestRunner:
    """Comprehensive test runner for ScriptCraft."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            'unit_tests': {},
            'integration_tests': {},
            'system_tests': {},
            'tool_tests': {},
            'performance_tests': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'duration': 0
            }
        }
        self.start_time = time.time()
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{timestamp}] {level}: {message}")
    
    def run_pytest(self, test_path: str, category: str = "general") -> Dict:
        """Run pytest on a specific test path."""
        self.log(f"Running pytest on {test_path}")
        
        cmd = [
            sys.executable, "-m", "pytest", test_path,
            "--tb=short",
            "--quiet",
            "--json-report",
            "--json-report-file=none"
        ]
        
        if not self.verbose:
            cmd.append("--capture=no")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=300  # 5 minute timeout
            )
            
            # Parse results
            test_result = {
                'path': test_path,
                'category': category,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
            if test_result['success']:
                self.log(f"✅ {test_path} passed", "INFO")
            else:
                self.log(f"❌ {test_path} failed", "ERROR")
                if self.verbose:
                    print(f"STDOUT: {result.stdout}")
                    print(f"STDERR: {result.stderr}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            self.log(f"⏰ {test_path} timed out", "ERROR")
            return {
                'path': test_path,
                'category': category,
                'return_code': -1,
                'stdout': '',
                'stderr': 'Test timed out after 5 minutes',
                'success': False
            }
        except Exception as e:
            self.log(f"💥 {test_path} crashed: {e}", "ERROR")
            return {
                'path': test_path,
                'category': category,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def test_imports(self) -> Dict:
        """Test that all ScriptCraft modules can be imported."""
        self.log("Testing imports...")
        
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
            ('scriptcraft.enhancements', 'Enhancements package'),
        ]
        
        results = {}
        for module_name, description in import_tests:
            try:
                __import__(module_name)
                self.log(f"✅ {description} imports successfully")
                results[module_name] = {'success': True, 'description': description}
            except ImportError as e:
                self.log(f"❌ {description} import failed: {e}", "ERROR")
                results[module_name] = {'success': False, 'error': str(e), 'description': description}
            except Exception as e:
                self.log(f"💥 {description} import crashed: {e}", "ERROR")
                results[module_name] = {'success': False, 'error': str(e), 'description': description}
        
        return results
    
    def test_tool_imports(self) -> Dict:
        """Test that all tools can be imported."""
        self.log("Testing tool imports...")
        
        # Get all available tools
        try:
            from scriptcraft.tools import get_available_tools
            tools = get_available_tools()
        except Exception as e:
            self.log(f"❌ Failed to get available tools: {e}", "ERROR")
            return {}
        
        results = {}
        for tool_name, tool_info in tools.items():
            try:
                # Try to import the tool class
                tool_class = tool_info.get('class')
                if tool_class:
                    # Test instantiation
                    instance = tool_class()
                    self.log(f"✅ {tool_name} imports and instantiates successfully")
                    results[tool_name] = {'success': True, 'class': tool_class.__name__}
                else:
                    self.log(f"⚠️ {tool_name} has no class information", "WARNING")
                    results[tool_name] = {'success': False, 'error': 'No class information'}
            except Exception as e:
                self.log(f"❌ {tool_name} import failed: {e}", "ERROR")
                results[tool_name] = {'success': False, 'error': str(e)}
        
        return results
    
    def run_unit_tests(self) -> Dict:
        """Run all unit tests."""
        self.log("Running unit tests...")
        
        unit_test_paths = [
            "tests/test_base_tools.py",
            "tests/test_tool_registry.py",
            "tests/test_registry.py",
            "tests/test_pipeline_utils.py",
        ]
        
        results = {}
        for test_path in unit_test_paths:
            if Path(test_path).exists():
                result = self.run_pytest(test_path, "unit")
                results[test_path] = result
            else:
                self.log(f"⚠️ {test_path} not found", "WARNING")
        
        return results
    
    def run_tool_tests(self) -> Dict:
        """Run tests for individual tools."""
        self.log("Running tool tests...")
        
        tool_test_paths = [
            "tests/tools/test_automated_labeler.py",
            "tests/tools/test_data_content_comparer.py",
            "tests/tools/test_rhq_form_autofiller.py",
            "tests/tools/test_schema_detector.py",
        ]
        
        results = {}
        for test_path in tool_test_paths:
            if Path(test_path).exists():
                result = self.run_pytest(test_path, "tool")
                results[test_path] = result
            else:
                self.log(f"⚠️ {test_path} not found", "WARNING")
        
        return results
    
    def run_integration_tests(self) -> Dict:
        """Run integration tests."""
        self.log("Running integration tests...")
        
        integration_test_paths = [
            "tests/integration/test_release_consistency.py",
            "tests/integration/test_feature_change_checker.py",
            "tests/integration/test_dictionary_driven_checker.py",
        ]
        
        results = {}
        for test_path in integration_test_paths:
            if Path(test_path).exists():
                result = self.run_pytest(test_path, "integration")
                results[test_path] = result
            else:
                self.log(f"⚠️ {test_path} not found", "WARNING")
        
        return results
    
    def run_system_tests(self) -> Dict:
        """Run system tests."""
        self.log("Running system tests...")
        
        # For now, just check if system test directory exists
        system_test_dir = Path("tests/system")
        if system_test_dir.exists():
            result = self.run_pytest("tests/system", "system")
            return {"tests/system": result}
        else:
            self.log("⚠️ No system tests found", "WARNING")
            return {}
    
    def run_performance_tests(self) -> Dict:
        """Run performance tests."""
        self.log("Running performance tests...")
        
        performance_test_paths = [
            "tests/performance/test_checkers_performance.py",
        ]
        
        results = {}
        for test_path in performance_test_paths:
            if Path(test_path).exists():
                result = self.run_pytest(test_path, "performance")
                results[test_path] = result
            else:
                self.log(f"⚠️ {test_path} not found", "WARNING")
        
        return results
    
    def run_all_tests(self, category: Optional[str] = None, tool: Optional[str] = None):
        """Run all tests or specific categories."""
        self.log("🚀 Starting comprehensive test run...")
        
        # Test imports first
        self.results['imports'] = self.test_imports()
        self.results['tool_imports'] = self.test_tool_imports()
        
        if category is None or category == "unit":
            self.results['unit_tests'] = self.run_unit_tests()
        
        if category is None or category == "tools":
            self.results['tool_tests'] = self.run_tool_tests()
        
        if category is None or category == "integration":
            self.results['integration_tests'] = self.run_integration_tests()
        
        if category is None or category == "system":
            self.results['system_tests'] = self.run_system_tests()
        
        if category is None or category == "performance":
            self.results['performance_tests'] = self.run_performance_tests()
        
        # Calculate summary
        self.calculate_summary()
        
        # Print results
        self.print_summary()
        
        return self.results
    
    def calculate_summary(self):
        """Calculate test summary statistics."""
        total_tests = 0
        passed = 0
        failed = 0
        errors = 0
        
        for category in ['unit_tests', 'tool_tests', 'integration_tests', 'system_tests', 'performance_tests']:
            for test_name, result in self.results[category].items():
                total_tests += 1
                if result['success']:
                    passed += 1
                else:
                    failed += 1
                    if result['return_code'] == -1:
                        errors += 1
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'duration': time.time() - self.start_time
        }
    
    def print_summary(self):
        """Print test summary."""
        summary = self.results['summary']
        
        print("\n" + "="*60)
        print("🧪 SCRIPTCRAFT COMPREHENSIVE TEST RESULTS")
        print("="*60)
        
        # Import results
        print("\n📦 IMPORT TESTS:")
        import_success = sum(1 for r in self.results['imports'].values() if r['success'])
        import_total = len(self.results['imports'])
        print(f"   Core modules: {import_success}/{import_total} ✅")
        
        tool_import_success = sum(1 for r in self.results['tool_imports'].values() if r['success'])
        tool_import_total = len(self.results['tool_imports'])
        print(f"   Tools: {tool_import_success}/{tool_import_total} ✅")
        
        # Test results by category
        print("\n🧪 TEST RESULTS BY CATEGORY:")
        for category in ['unit_tests', 'tool_tests', 'integration_tests', 'system_tests', 'performance_tests']:
            category_results = self.results[category]
            if category_results:
                success_count = sum(1 for r in category_results.values() if r['success'])
                total_count = len(category_results)
                status = "✅" if success_count == total_count else "❌"
                print(f"   {category.replace('_', ' ').title()}: {success_count}/{total_count} {status}")
        
        # Overall summary
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed']} ✅")
        print(f"   Failed: {summary['failed']} ❌")
        print(f"   Errors: {summary['errors']} 💥")
        print(f"   Duration: {summary['duration']:.2f}s")
        
        success_rate = (summary['passed'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if summary['failed'] == 0 and summary['errors'] == 0:
            print("\n🎉 ALL TESTS PASSED! ScriptCraft is ready for production!")
        else:
            print(f"\n⚠️ {summary['failed']} tests failed. Please review the errors above.")
        
        print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run comprehensive ScriptCraft tests")
    parser.add_argument("--category", choices=["unit", "tools", "integration", "system", "performance"], 
                       help="Run specific test category")
    parser.add_argument("--tool", help="Run tests for specific tool")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(verbose=args.verbose)
    
    # Run tests
    results = runner.run_all_tests(category=args.category, tool=args.tool)
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to {args.output}")
    
    # Exit with appropriate code
    summary = results['summary']
    if summary['failed'] > 0 or summary['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 