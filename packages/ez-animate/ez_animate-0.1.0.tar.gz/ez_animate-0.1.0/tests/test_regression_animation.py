import os
import sys
import unittest
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.utils import BaseTest, suppress_print

from ez_animate import (
    RegressionAnimation,
)
from sega_learn.linear_models import Ridge
from sega_learn.utils import (
    Metrics,
    make_regression,
)


class TestRegressionAnimation(BaseTest):
    """Unit test for the RegressionAnimation class."""

    def test_keep_previous_max_previous_behavior(self):
        """Test keep_previous and max_previous logic in update_plot."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            keep_previous=True,
            max_previous=2,
        )
        animator.setup_plot("Test Regression", "Feature", "Target")
        animator.update_model(100)
        # Simulate multiple frames to trigger previous_predicted_lines logic
        for frame in [100, 200, 300, 400]:
            animator.update_model(frame)
            animator.update_plot(frame)
        self.assertLessEqual(len(animator.previous_predicted_lines), 3)
        plt.close(animator.fig)

    def test_metric_progression_and_lines(self):
        """Test metric progression and metric_lines logic in update_plot."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"alpha": 1.0},
            metric_fn=[Metrics.mean_squared_error, Metrics.r_squared],
            plot_metric_progression=True,
            max_metric_subplots=2,
        )
        animator.setup_plot("Test Regression", "Feature", "Target")
        animator.metric_progression = [[], []]
        # Simulate metric_lines for blitting
        from matplotlib.lines import Line2D

        animator.metric_lines = [Line2D([], []), Line2D([], [])]
        animator.update_model(100)
        result = animator.update_plot(100)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        plt.close(animator.fig)

    def test_static_parameters_none_defaults_to_dict(self):
        """Test that static_parameters=None results in an empty dict."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters=None,
        )
        self.assertIsInstance(animator.static_parameters, dict)

    def test_pca_1d_input_no_pca(self):
        """Test that 1D input does not trigger PCA."""
        X_1d = np.random.rand(100, 1)
        y_1d = np.random.rand(100)
        animator = RegressionAnimation(
            model=Ridge,
            X=X_1d,
            y=y_1d,
            test_size=0.25,
            dynamic_parameter="max_iter",
            pca_components=1,
        )
        self.assertFalse(animator.needs_pca)
        self.assertIsNone(animator.pca_instance)

    def test_update_plot_no_metric_fn(self):
        """Test update_plot when metric_fn is None."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
        )
        animator.setup_plot("Test Regression", "Feature", "Target")
        animator.update_model(100)
        # Should not raise or print metric info
        result = animator.update_plot(100)
        self.assertIsInstance(result, tuple)
        plt.close(animator.fig)

    @classmethod
    def setUpClass(cls):  # NOQA D201
        """Initializes the test suite."""
        print("\nTesting RegressionAnimation Class", end="", flush=True)
        mpl.use("Agg")

    def setUp(self):  # NOQA D201
        """Prepares each test."""
        # Generate synthetic regression data
        self.X, self.y = make_regression(
            n_samples=100, n_features=1, noise=0.5, random_state=42
        )
        warnings.filterwarnings("ignore", category=UserWarning)

    def test_init(self):
        """Test RegressionAnimation initialization."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"alpha": 1.0},
            keep_previous=True,
        )
        self.assertIsInstance(animator.X_train, np.ndarray)
        self.assertIsInstance(animator.y_train, np.ndarray)
        self.assertIsInstance(animator.X_test, np.ndarray)
        self.assertIsInstance(animator.y_test, np.ndarray)

    def test_init_with_invalid_Xy(self):
        """Test initialization with invalid X or y."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=None,
                y=self.y,
                test_size=0.25,
                dynamic_parameter="max_iter",
            )
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=None,
                test_size=0.25,
                dynamic_parameter="max_iter",
            )

    def test_init_with_invalid_max_subplots(self):
        """Test initialization with invalid max_subplots."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=0.25,
                dynamic_parameter="max_iter",
                max_metric_subplots=-1,
            )
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=0.25,
                dynamic_parameter="max_iter",
                max_metric_subplots=0,
            )

    def test_init_with_invalid_test_size(self):
        """Test initialization with invalid test_size."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=-0.1,
                dynamic_parameter="max_iter",
            )
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=1.5,
                dynamic_parameter="max_iter",
            )

    def test_init_with_invalid_dynamic_parameter(self):
        """Test initialization with invalid dynamic_parameter."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=0.25,
                dynamic_parameter=3,
            )

    def test_init_with_invalid_static_parameters(self):
        """Test initialization with invalid static_parameters."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=0.25,
                dynamic_parameter="max_iter",
                static_parameters=["invalid_param"],
            )

    def test_init_with_invalid_keep_previous(self):
        """Test initialization with invalid keep_previous."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=0.25,
                dynamic_parameter="max_iter",
                keep_previous="invalid_value",
            )

    def test_init_with_invalid_max_previous(self):
        """Test initialization with invalid max_previous."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=0.25,
                dynamic_parameter="max_iter",
                max_previous=1.5,
            )

    def test_init_with_invalid_pca_components(self):
        """Test initialization with invalid pca_components."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=0.25,
                dynamic_parameter="max_iter",
                pca_components=-1,
            )
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=0.25,
                dynamic_parameter="max_iter",
                pca_components=1.5,
            )

    def test_init_with_pca(self):
        """Test initialization with PCA for multi-feature data."""
        # Create multi-feature data
        X_multi = np.random.rand(100, 5)
        y_multi = np.random.rand(100)

        with suppress_print():
            animator = RegressionAnimation(
                model=Ridge,
                X=X_multi,
                y=y_multi,
                test_size=0.25,
                dynamic_parameter="max_iter",
                pca_components=1,
            )
        self.assertTrue(animator.needs_pca)
        self.assertIsNotNone(animator.pca_instance)
        self.assertEqual(
            animator.X_train.shape[1], 1
        )  # Should be reduced to 1 component

    def test_init_no_dynamic_parameter(self):
        """Test initialization with no dynamic parameter."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=self.y,
                test_size=0.25,
                dynamic_parameter=None,
                keep_previous=True,
            )

    def test_init_no_static_parameters(self):
        """Test initialization with no static parameters."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters=None,
            keep_previous=True,
        )
        self.assertIsNotNone(animator)
        self.assertDictEqual(animator.static_parameters, {})

    def test_init_no_X(self):
        """Test initialization with no X."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=None,
                y=self.y,
                test_size=0.25,
                dynamic_parameter="max_iter",
                keep_previous=True,
            )

    def test_init_no_y(self):
        """Test initialization with no y."""
        with self.assertRaises(ValueError):
            RegressionAnimation(
                model=Ridge,
                X=self.X,
                y=None,
                test_size=0.25,
                dynamic_parameter="max_iter",
                keep_previous=True,
            )

    def test_setup_plot(self):
        """Test setup_plot with valid parameters."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
        )
        animator.setup_plot("Test Regression", "Feature", "Target")
        self.assertIsNotNone(animator.fig)
        self.assertIsNotNone(animator.ax)
        self.assertEqual(animator.ax.get_title(), "Test Regression")
        self.assertIsNotNone(animator.scatter_points)
        self.assertIsNotNone(animator.scatter_points_test)
        self.assertIsNotNone(animator.predicted_line)
        plt.close(animator.fig)

    def test_setup_plot_with_pca(self):
        """Test setup_plot with PCA."""
        # X that requires PCA
        X = np.random.rand(100, 5)
        y = np.random.rand(100)
        animator = RegressionAnimation(
            model=Ridge,
            X=X,
            y=y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            pca_components=1,
        )
        animator.setup_plot("Test Regression with PCA", "Feature", "Target")
        self.assertIsNotNone(animator.fig)
        self.assertIsNotNone(animator.ax)
        self.assertEqual(animator.ax.get_title(), "Test Regression with PCA")
        self.assertIsNotNone(animator.scatter_points)
        self.assertIsNotNone(animator.scatter_points_test)
        self.assertIsNotNone(animator.predicted_line)
        plt.close(animator.fig)

    def test_update_model(self):
        """Test update_model with valid frame parameter."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"alpha": 1.0},
        )
        with suppress_print():
            # Test with a specific max_iter value
            animator.update_model(1000)
        self.assertIsInstance(animator.model_instance, Ridge)
        self.assertEqual(animator.model_instance.max_iter, 1000)
        self.assertEqual(animator.model_instance.alpha, 1.0)
        self.assertIsInstance(animator.X_test_sorted, np.ndarray)
        self.assertIsInstance(animator.predicted_values, np.ndarray)

    def test_update_plot_with_metrics(self):
        """Test update_plot with metrics."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"alpha": 1.0},
            metric_fn=[Metrics.mean_squared_error, Metrics.r_squared],
        )
        with suppress_print():
            animator.setup_plot("Test Regression", "Feature", "Target")
            animator.update_model(1000)

            # Check that update_plot returns a tuple of artists
            artists = animator.update_plot(1000)

        self.assertIsInstance(artists, tuple)
        self.assertEqual(len(artists), 1)
        self.assertIsInstance(artists[0], plt.Line2D)
        plt.close(animator.fig)

    def test_update_plot_with_no_metrics(self):
        """Test update_plot without metrics."""
        animator = RegressionAnimation(
            model=Ridge,
            X=self.X,
            y=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"alpha": 1.0},
        )
        with suppress_print():
            animator.setup_plot("Test Regression", "Feature", "Target")
            animator.update_model(1000)

            # Check that update_plot returns a tuple of artists
            artists = animator.update_plot(1000)

        self.assertIsInstance(artists, tuple)
        self.assertEqual(len(artists), 1)
        self.assertIsInstance(artists[0], plt.Line2D)
        plt.close(animator.fig)


if __name__ == "__main__":
    unittest.main()
