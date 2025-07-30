import os
import sys
import unittest

# Change the working directory to the parent directory to allow importing the package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tests.utils import BaseTest

from ez_animate import *


class TestImports(BaseTest):
    """Tests that the main package can be imported correctly."""

    @classmethod
    def setUpClass(cls):  # NOQA D201
        print("\nTesting Package Imports", end="", flush=True)

    def test_all_imports(self):
        """Test that all expected imports are available in the package."""
        import ez_animate

        self.assertIsNotNone(ez_animate)
        self.assertTrue(hasattr(ez_animate, "__version__"))

        # Animation Classes
        self.assertTrue(hasattr(ez_animate, "ClassificationAnimation"))
        self.assertTrue(hasattr(ez_animate, "ForecastingAnimation"))
        self.assertTrue(hasattr(ez_animate, "RegressionAnimation"))

        # Utility Functions
        self.assertTrue(hasattr(ez_animate, "PCA"))
        self.assertTrue(hasattr(ez_animate, "train_test_split"))

    def test_all_imports_from_init(self):
        """Test that all expected attributes are imported in __init__.py."""
        import ez_animate

        expected_all = [
            "ForecastingAnimation",
            "RegressionAnimation",
            "ClassificationAnimation",
            "ClusteringAnimation",
            "PCA",
            "train_test_split",
        ]
        self.assertListEqual(expected_all, ez_animate.__all__)

    def test_imports_from_animator(self):
        """Test that animation classes can be imported correctly."""
        from ez_animate import (
            ClassificationAnimation,
            ClusteringAnimation,
            ForecastingAnimation,
            RegressionAnimation,
        )

        self.assertIsNotNone(ClassificationAnimation)
        self.assertIsNotNone(ForecastingAnimation)
        self.assertIsNotNone(RegressionAnimation)
        self.assertIsNotNone(ClusteringAnimation)

    def test_imports_from_utils(self):
        """Test that utility functions can be imported correctly."""
        from ez_animate.utils import PCA, train_test_split

        self.assertIsNotNone(PCA)
        self.assertIsNotNone(train_test_split)

    def test_imports_from_widcard(self):
        """Test that wildcard imports work correctly."""
        self.assertIsNotNone(ForecastingAnimation)
        self.assertIsNotNone(RegressionAnimation)
        self.assertIsNotNone(ClassificationAnimation)
        self.assertIsNotNone(ClusteringAnimation)
        self.assertIsNotNone(PCA)
        self.assertIsNotNone(train_test_split)


if __name__ == "__main__":
    unittest.main()
