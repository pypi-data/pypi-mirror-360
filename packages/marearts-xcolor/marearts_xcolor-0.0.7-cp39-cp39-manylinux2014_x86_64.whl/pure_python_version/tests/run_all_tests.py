#!/usr/bin/env python3
"""
Comprehensive test runner for MareArts XColor Pure Python implementation
"""

import sys
import os
import importlib.util

def run_test_module(module_name, module_path):
    """Run a test module and return success status"""
    print(f"\n{'='*60}")
    print(f"Running {module_name}")
    print(f"{'='*60}")
    
    try:
        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Run the main test function
        if hasattr(module, 'run_all_basic_tests'):
            return module.run_all_basic_tests()
        elif hasattr(module, 'run_all_gpu_tests'):
            return module.run_all_gpu_tests()
        elif hasattr(module, 'run_all_analysis_tests'):
            return module.run_all_analysis_tests()
        else:
            print(f"Warning: No main test function found in {module_name}")
            return True
            
    except Exception as e:
        print(f"Error running {module_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests for pure Python implementation"""
    print("MareArts XColor Pure Python Implementation Test Suite")
    print("=" * 60)
    
    # Get the directory containing this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define test modules to run
    test_modules = [
        ('Basic Functionality Tests', os.path.join(test_dir, 'test_basic_functionality.py')),
        ('GPU Support Tests', os.path.join(test_dir, 'test_gpu_support.py')),
        ('Color Analysis Tests', os.path.join(test_dir, 'test_color_analysis.py'))
    ]
    
    # Run all tests
    results = []
    for module_name, module_path in test_modules:
        if os.path.exists(module_path):
            success = run_test_module(module_name, module_path)
            results.append((module_name, success))
        else:
            print(f"Warning: Test file not found: {module_path}")
            results.append((module_name, False))
    
    # Print final summary
    print(f"\n{'='*60}")
    print("FINAL TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for module_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{module_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All test suites passed successfully!")
        return 0
    else:
        print("❌ Some test suites failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())