import os
import random
import sys
import unittest
from contextlib import contextmanager

import numpy as np


@contextmanager
def suppress_print():
    """A context manager that suppresses all print statements within its block.

    This function redirects the standard output to os.devnull, silencing any print statements executed within its context.
    Once the context is exited, the standard output is restored to its original state.
    Usage:
        with suppress_print():
            # Any print statements here will be suppressed
    Yields:
        None
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def strip_file_path(file_path):
    """Strips the file path and returns the file name."""
    return os.path.basename(file_path)


class BaseTest(unittest.TestCase):
    """Base class for all test cases."""

    @classmethod
    def setUpClass(cls):
        """Set up the class for all test cases."""
        super().setUpClass()
        np.random.seed(42)
        random.seed(42)
