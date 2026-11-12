"""
    This script is used to run all the unit tests in the `tests` directory. 
    It discovers and runs all test cases that match the pattern `*_test.py`. 
    The results of the tests are printed to the console, and the script exits
    with a status code indicating whether all tests passed or if any failed.

    As the above description shows, the script essentially does what the following
    command does:
    python -m unittest discover -s tests -p "*_test.py" -v

    The whole reason for the script is to make it easier to run tests (a.k.a. not having
    to type in the long command above).
"""
from pathlib import Path
import sys
import unittest

if __name__ == "__main__":
    tests_dir = Path(__file__).parent / "tests"
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(tests_dir),
        pattern="*_test.py",
        top_level_dir=str(tests_dir),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())