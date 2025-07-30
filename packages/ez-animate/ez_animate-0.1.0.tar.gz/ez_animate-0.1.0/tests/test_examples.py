import os
import sys

# Add the project root to sys.path to allow 'tests' imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import contextlib
import importlib.util
import io
import unittest
from pathlib import Path

import matplotlib.pyplot as plt
from tests.utils import BaseTest, strip_file_path

# Change the working directory to the parent directory to allow importing the main module.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# List of test exceptions for specific example files that should be tested separately.
TEST_EXCEPTIONS = []


# Patch plt.show to avoid warnings in test environment
plt.show = lambda *args, **kwargs: None


def make_example_test(example_file):
    """Creates a test function for a given example file that imports and executes it."""

    def test_func(self):
        """Tests the functionality of a given example file by importing it as a module and executing it."""
        print(
            f"\nTesting example file: {strip_file_path(example_file)}",
            end="",
            flush=True,
        )
        spec = importlib.util.spec_from_file_location("module.name", example_file)
        example_module = importlib.util.module_from_spec(spec)
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(example_module)

    return test_func


def make_exception_test(example_file):
    """Creates a test function for a given example file that is expected to raise an exception."""

    def test_func(self):
        # Placeholder for exception-specific test logic
        # You can customize this as needed
        print(
            f"\nTesting exception example file: {strip_file_path(example_file)}",
            end="",
            flush=True,
        )
        spec = importlib.util.spec_from_file_location("module.name", example_file)
        example_module = importlib.util.module_from_spec(spec)
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(example_module)

    return test_func


class TestExampleExceptions(BaseTest):
    """Test cases to check for exceptions in example files. Test methods are added dynamically."""


class ExampleFileTests(BaseTest):
    """Test cases for the example files. Holds dynamically generated test cases for each example file."""


# Dynamically generate test cases for each example file at import time (for pytest compatibility)
examples_dir = Path(__file__).parent.parent / "examples"
example_files = list(examples_dir.glob("**/*.py"))

if not example_files:
    raise FileNotFoundError("No example files found.")
test_exceptions = [f"test_{name}" for name in TEST_EXCEPTIONS]
for example_file in example_files:
    test_name = f"test_{os.path.basename(example_file)}"
    if test_name in test_exceptions:
        setattr(TestExampleExceptions, test_name, make_exception_test(example_file))
    else:
        setattr(ExampleFileTests, test_name, make_example_test(example_file))


def load_tests(loader, tests, pattern):
    """Load test cases for each example file."""
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(ExampleFileTests))
    suite.addTests(loader.loadTestsFromTestCase(TestExampleExceptions))
    return suite


if __name__ == "__main__":
    unittest.main()
