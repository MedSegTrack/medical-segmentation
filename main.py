import os
import unittest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'test')))

def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='test', pattern='test_*.py')
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    # Run the tests
    run_tests()