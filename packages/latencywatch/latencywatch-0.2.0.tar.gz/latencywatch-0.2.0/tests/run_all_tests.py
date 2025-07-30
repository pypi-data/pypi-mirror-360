import importlib
import os
import sys
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str = ""
    output: str = ""

def run_test(test_file: str) -> TestResult:
    """Run a test file and return the result."""
    test_name = os.path.basename(test_file).replace('.py', '')
    result = TestResult(name=test_name, passed=False)
    
    try:
        # Import the test module
        spec = importlib.util.spec_from_file_location(test_name, test_file)
        test_module = importlib.util.module_from_spec(spec)
        sys.modules[test_name] = test_module
        spec.loader.exec_module(test_module)
        
        # First try to get a function with the same name as the file
        test_func = getattr(test_module, test_name, None)
        
        # If not found, look for a function called 'run_test' or 'test'
        if not test_func or not callable(test_func):
            test_func = getattr(test_module, 'run_test', 
                             getattr(test_module, 'test', None))
        
        # If still not found, check if there's a main function that runs the test
        if not test_func or not callable(test_func):
            if hasattr(test_module, 'root_function') and callable(test_module.root_function):
                test_func = test_module.root_function
            else:
                return TestResult(
                    name=test_name,
                    passed=False,
                    message=f"❌ No test function found in {test_name}.py. "
                            f"Expected a function named '{test_name}', 'run_test', 'test', or 'root_function'"
                )
        
        # Run the test
        test_func()
        result.passed = True
        result.message = "✅ Test passed"
        
    except Exception as e:
        import traceback
        result.message = f"❌ Test failed: {str(e)}\n{traceback.format_exc()}"
    
    return result

def main():
    # Find all test files
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_files = [
        os.path.join(test_dir, f) 
        for f in os.listdir(test_dir) 
        if f.startswith('test_') and f.endswith('.py') and f != 'run_all_tests.py'
    ]
    
    print("\n" + "=" * 50)
    print(f"Running {len(test_files)} test(s)")
    print("=" * 50 + "\n")
    
    # Run all tests
    results = []
    for test_file in test_files:
        print(f"Running {os.path.basename(test_file)}...")
        result = run_test(test_file)
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(f"  {status}: {result.message}\n")
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    for result in results:
        status = "✅" if result.passed else "❌"
        print(f"{status} {result.name}: {result.message}")
    
    passed = sum(1 for r in results if r.passed)
    print(f"\nPassed: {passed}/{len(results)}")

if __name__ == "__main__":
    # Add parent directory to path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    main()