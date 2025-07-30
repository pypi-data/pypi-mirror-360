#!/usr/bin/env python3
"""
Test script to verify grasp_sdk installation and basic functionality.

Usage:
    python test_install.py
"""

import sys
import importlib
from typing import List


def test_import(module_name: str) -> bool:
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing {module_name}: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality of the package."""
    try:
        from grasp_sdk import GraspServer, launch_browser
        print("✅ Main classes imported successfully")
        
        # Test GraspServer instantiation
        server = GraspServer()
        print("✅ GraspServer instantiated successfully")
        
        # Test basic properties
        status = server.get_status()
        print(f"✅ Server status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing grasp_sdk installation...\n")
    
    # Test core module imports
    modules_to_test = [
        'grasp_sdk',
        'grasp_sdk.models',
        'grasp_sdk.services',
        'grasp_sdk.utils',
    ]
    
    import_results = []
    for module in modules_to_test:
        result = test_import(module)
        import_results.append(result)
    
    print()
    
    # Test basic functionality
    functionality_test = test_basic_functionality()
    
    print()
    
    # Summary
    total_tests = len(import_results) + 1
    passed_tests = sum(import_results) + (1 if functionality_test else 0)
    
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! grasp_sdk is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())