#!/usr/bin/env python
"""
Test runner with detailed summary
"""
import os
import sys
import django
from io import StringIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test.runner import DiscoverRunner

if __name__ == "__main__":
    # Create test runner
    runner = DiscoverRunner(verbosity=2)
    
    # Run tests
    print("Running Task Analyzer Unit Tests...")
    print("="*60)
    
    failures = runner.run_tests(["tasks.tests.ScoringAlgorithmTestCase"])
    
    # Count total tests
    from tasks.tests import ScoringAlgorithmTestCase
    import unittest
    
    suite = unittest.TestLoader().loadTestsFromTestCase(ScoringAlgorithmTestCase)
    total_tests = suite.countTestCases()
    passed_tests = total_tests - failures
    
    # Print summary
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {passed_tests} out of {total_tests} tests passing")
    print("="*60)
    
    if failures == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {failures} test(s) failed")
    
    print("="*60)
    sys.exit(failures)
