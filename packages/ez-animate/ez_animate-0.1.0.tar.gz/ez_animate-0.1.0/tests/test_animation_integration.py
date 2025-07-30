import os
import sys
import unittest
from unittest.mock import patch

import matplotlib as mpl
import matplotlib.pyplot as plt  # Added for closing figures
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.utils import BaseTest, suppress_print

from ez_animate import (
    ClassificationAnimation,
    ClusteringAnimation,
    ForecastingAnimation,
    RegressionAnimation,
)
from ez_animate.animation_base import AnimationBase
from sega_learn.clustering import KMeans
from sega_learn.linear_models import LogisticRegression, Ridge
from sega_learn.time_series.moving_average import ExponentialMovingAverage
from sega_learn.utils import (
    Metrics,
    make_classification,
    make_regression,
    make_time_series,
)


class TestAnimationBase(BaseTest):
    """Base class for animation tests."""

    def test_update_metric_plot_basic(self):
        """Test update_metric_plot updates metric lines and annotations correctly."""

        class DummyAnimation(AnimationBase):
            def update_model(self, frame):
                pass

            def update_plot(self, frame):
                pass

        # Dummy metric function
        def dummy_metric(y_true, y_pred):
            return np.sum(y_true) + np.sum(y_pred)

        dummy = DummyAnimation(
            model=None,
            train_series=[1, 2, 3],
            test_series=[4, 5, 6],
            dynamic_parameter="param",
            static_parameters={},
            keep_previous=False,
            metric_fn=[dummy_metric],
            plot_metric_progression=True,
            max_metric_subplots=1,
        )
        dummy.setup_plot("Title", "X", "Y")
        # Simulate metric progression
        dummy.metric_progression[0].extend([1.0, 2.0, 3.0])
        dummy.update_metric_plot(frame=2)
        # Check that metric line data matches progression
        x_data, y_data = dummy.metric_lines[0].get_data()
        self.assertTrue(np.array_equal(x_data, np.arange(3)))
        self.assertTrue(np.array_equal(y_data, np.array([1.0, 2.0, 3.0])))
        # Check annotation exists and value is correct
        annotation = getattr(dummy.metric_axes[0], "_current_metric_annotation", None)
        self.assertIsNotNone(annotation)
        self.assertIn("3", annotation.get_text())
        plt.close(dummy.fig)

    def test_update_metric_plot_empty(self):
        """Test update_metric_plot with empty progression does not fail and annotation is None."""

        class DummyAnimation(AnimationBase):
            def update_model(self, frame):
                pass

            def update_plot(self, frame):
                pass

        def dummy_metric(y_true, y_pred):
            return 0

        dummy = DummyAnimation(
            model=None,
            train_series=[1, 2, 3],
            test_series=[4, 5, 6],
            dynamic_parameter="param",
            static_parameters={},
            keep_previous=False,
            metric_fn=[dummy_metric],
            plot_metric_progression=True,
            max_metric_subplots=1,
        )
        dummy.setup_plot("Title", "X", "Y")
        # metric_progression is empty
        dummy.update_metric_plot(frame=0)
        annotation = getattr(dummy.metric_axes[0], "_current_metric_annotation", None)
        self.assertIsNone(annotation)
        plt.close(dummy.fig)

    @classmethod
    def setUpClass(cls):  # NOQA D201
        """Initializes the test suite."""
        print("\nTesting Animation Base", end="", flush=True)
        mpl.use("Agg")

    def test_abstract_methods_raise_type_error(self):
        """Test that instantiating AnimationBase directly raises TypeError due to abstract methods."""
        from ez_animate.animation_base import AnimationBase

        with self.assertRaises(TypeError):
            AnimationBase(
                model=None,
                train_series=[1],
                test_series=[1],
                dynamic_parameter="param",
                static_parameters={},
                keep_previous=False,
            )

    def test_abstract_methods_raise_not_implemented(self):
        """Test that calling update_model and update_plot on a dummy subclass raises NotImplementedError."""
        from ez_animate.animation_base import AnimationBase

        class DummyAnimation(AnimationBase):
            def update_model(self, frame):
                return super().update_model(frame)

            def update_plot(self, frame):
                return super().update_plot(frame)

        dummy = DummyAnimation(
            model=None,
            train_series=[1],
            test_series=[1],
            dynamic_parameter="param",
            static_parameters={},
            keep_previous=False,
        )
        with self.assertRaises(NotImplementedError):
            dummy.update_model(0)
        with self.assertRaises(NotImplementedError):
            dummy.update_plot(0)

    def test_save_no_animation(self):
        """Test that save() raises an error if no animation exists."""
        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=np.array([1, 2, 3]),
            test_series=np.array([4, 5, 6]),
            forecast_steps=3,
            dynamic_parameter="alpha",
        )
        with self.assertRaises(RuntimeError):
            animator.save("test_animation.mp4")
        plt.close(animator.fig)


class TestAnimationIntegration(BaseTest):
    """Integration tests for animation classes."""

    @classmethod
    def setUpClass(cls):  # NOQA D201
        """Initializes the test suite."""
        print("\nTesting Animation Integration", end="", flush=True)
        mpl.use("Agg")

    @patch("matplotlib.animation.FuncAnimation")
    def test_forecasting_animate(self, mock_animation):
        """Test forecastingAnimation animate method."""
        # Generate a synthetic time series
        time_series = make_time_series(
            n_samples=1,
            n_timestamps=100,
            n_features=1,
            trend="linear",
            seasonality="sine",
            seasonality_period=10,
            noise=0.1,
            random_state=42,
        ).flatten()

        # Split into training and testing sets
        train_size = int(len(time_series) * 0.8)
        train_series = time_series[:train_size]
        test_series = time_series[train_size:]
        forecast_steps = len(test_series)

        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=train_series,
            test_series=test_series,
            forecast_steps=forecast_steps,
            dynamic_parameter="alpha",
            keep_previous=True,
            metric_fn=[Metrics.mean_squared_error],
        )

        animator.setup_plot("Test Forecasting", "Time", "Value")
        alpha_range = np.arange(0.01, 0.5, 0.1)

        # Test animate method with mock
        animation = animator.animate(
            frames=alpha_range, interval=150, blit=True, repeat=False
        )
        self.assertEqual(animation, animator.ani)
        mock_animation.assert_called_once()
        plt.close(animator.fig)

    @patch("matplotlib.animation.FuncAnimation")
    def test_regression_animate(self, mock_animation):
        """Test RegressionAnimation animate method."""
        # Generate synthetic regression data
        X, y = make_regression(n_samples=100, n_features=1, noise=0.5, random_state=42)

        animator = RegressionAnimation(
            model=Ridge,
            X=X,
            y=y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"alpha": 1.0},
            keep_previous=True,
            metric_fn=[Metrics.mean_squared_error],
        )

        animator.setup_plot("Test Regression", "Feature", "Target")
        max_iter_range = range(100, 1000, 100)

        # Test animate method with mock
        animation = animator.animate(
            frames=max_iter_range, interval=150, blit=True, repeat=False
        )
        self.assertEqual(animation, animator.ani)
        mock_animation.assert_called_once()
        plt.close(animator.fig)

    @patch("matplotlib.animation.FuncAnimation")
    def test_classification_animate(self, mock_animation):
        """Test ClassificationAnimation animate method."""
        # Generate synthetic classification data
        X, y = make_classification(
            n_samples=100,
            n_features=2,
            n_redundant=0,
            n_informative=2,
            n_classes=2,
            random_state=42,
        )

        animator = ClassificationAnimation(
            model=LogisticRegression,
            X=X,
            y=y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"learning_rate": 0.001},
            keep_previous=True,
            metric_fn=[Metrics.accuracy],
        )

        animator.setup_plot("Test Classification", "Feature 1", "Feature 2")
        max_iter_range = range(100, 1000, 100)

        # Test animate method with mock
        animation = animator.animate(
            frames=max_iter_range, interval=150, blit=True, repeat=False
        )
        self.assertEqual(animation, animator.ani)
        mock_animation.assert_called_once()
        plt.close(animator.fig)

    @patch("matplotlib.animation.FuncAnimation")
    def test_clustering_animate(self, mock_animation):
        """Test ClusteringAnimation animate method."""
        # Generate synthetic clustering data
        X, y = make_classification(
            n_samples=100,
            n_features=2,
            n_redundant=0,
            n_informative=2,
            n_classes=3,
            random_state=42,
        )

        animator = ClusteringAnimation(
            model=KMeans,
            data=X,
            labels=y,
            test_size=0.25,
            dynamic_parameter="n_iter",
            static_parameters={"n_clusters": 3},
            keep_previous=True,
            trace_centers=True,
        )

        animator.setup_plot("Test Clustering", "Feature 1", "Feature 2")
        n_iter_range = range(1, 10)

        # Test animate method with mock
        animation = animator.animate(
            frames=n_iter_range, interval=150, blit=True, repeat=False
        )
        self.assertEqual(animation, animator.ani)
        mock_animation.assert_called_once()
        plt.close(animator.fig)

    @patch("builtins.print")
    @patch("matplotlib.animation.FuncAnimation.save")
    def test_save_functionality(self, mock_save, mock_print):
        """Test the save functionality of animation classes."""
        # Generate synthetic regression data
        X, y = make_regression(n_samples=100, n_features=1, noise=0.5, random_state=42)

        animator = RegressionAnimation(
            model=Ridge, X=X, y=y, dynamic_parameter="max_iter"
        )

        animator.setup_plot("Test Regression", "Feature", "Target")

        # Mock the animation creation
        with patch("matplotlib.animation.FuncAnimation") as mock_animation:
            mock_instance = mock_animation.return_value
            animator.ani = mock_instance  # Set the animation attribute

            # Test saving
            animator.save("test.gif", writer="pillow", fps=5, dpi=100)
            mock_instance.save.assert_called_once_with(
                "test.gif", writer="pillow", fps=5, dpi=100
            )
            mock_print.assert_called_with("Animation saved successfully to test.gif.")
        plt.close(animator.fig)

    @patch("builtins.print")
    @patch("matplotlib.animation.FuncAnimation.save")
    def test_save_functionality_no_animation(self, mock_save, mock_print):
        """Assert RuntimeError when Animation has not been created."""
        # Generate synthetic regression data
        X, y = make_regression(n_samples=100, n_features=1, noise=0.5, random_state=42)

        animator = RegressionAnimation(
            model=Ridge, X=X, y=y, dynamic_parameter="max_iter"
        )

        animator.setup_plot("Test Regression", "Feature", "Target")
        with self.assertRaises(RuntimeError):
            # Attempt to save without creating an animation
            animator.save("test.gif", writer="pillow", fps=5, dpi=100)

        # If test.gif exists, remove it
        if os.path.exists("test.gif"):
            os.remove("test.gif")
        plt.close(animator.fig)

    @patch("builtins.print")
    def test_save_functionality_invalid_writer(self, mock_print):
        """Assert ValueError when an invalid writer is specified."""
        # Generate synthetic regression data
        X, y = make_regression(n_samples=100, n_features=1, noise=0.5, random_state=42)

        animator = RegressionAnimation(
            model=Ridge,
            X=X,
            y=y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"alpha": 1.0},
            keep_previous=True,
            metric_fn=[Metrics.mean_squared_error],
        )

        animator.setup_plot("Test Regression", "Feature", "Target")
        max_iter_range = range(100, 1000, 100)

        # Test animate method with mock
        animator.animate(frames=max_iter_range, interval=150, blit=True, repeat=False)

        with self.assertRaises(Exception) and suppress_print():
            # Attempt to save with an invalid writer
            animator.save("test.gif", writer="invalid_writer", fps=5, dpi=100)
        plt.close(animator.fig)

    @patch("builtins.print")
    def test_save_functionality_invalid_filename(self, mock_print):
        """Assert ValueError when an invalid filename is specified."""
        # Generate synthetic regression data
        X, y = make_regression(n_samples=100, n_features=1, noise=0.5, random_state=42)

        animator = RegressionAnimation(
            model=Ridge,
            X=X,
            y=y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"alpha": 1.0},
            keep_previous=True,
            metric_fn=[Metrics.mean_squared_error],
        )

        animator.setup_plot("Test Regression", "Feature", "Target")
        max_iter_range = range(100, 1000, 100)

        # Test animate method with mock
        animator.animate(frames=max_iter_range, interval=150, blit=True, repeat=False)

        with self.assertRaises(Exception) and suppress_print():
            # Attempt to save with an invalid writer
            animator.save("abc/test.xyz", writer="invalid_writer", fps=5, dpi=100)
        plt.close(animator.fig)

    @patch("matplotlib.pyplot.show")
    @patch("builtins.print")
    def test_show_success(self, mock_print, mock_show):
        """Test that show() displays the animation and prints success message."""
        X, y = make_regression(n_samples=10, n_features=1, noise=0.1, random_state=0)
        animator = RegressionAnimation(
            model=Ridge, X=X, y=y, dynamic_parameter="max_iter"
        )
        animator.setup_plot("Test", "X", "y")
        animator.ani = object()  # Simulate animation created
        animator.show()
        mock_show.assert_called_once()
        mock_print.assert_any_call("Animation displayed.")
        plt.close(animator.fig)

    def test_show_no_animation(self):
        """Test that show() raises RuntimeError if animation is not created."""
        X, y = make_regression(n_samples=10, n_features=1, noise=0.1, random_state=0)
        animator = RegressionAnimation(
            model=Ridge, X=X, y=y, dynamic_parameter="max_iter"
        )
        animator.setup_plot("Test", "X", "y")
        with self.assertRaises(RuntimeError):
            animator.show()
        plt.close(animator.fig)

    def test_show_no_figure(self):
        """Test that show() raises RuntimeError if plot is not set up."""
        X, y = make_regression(n_samples=10, n_features=1, noise=0.1, random_state=0)
        animator = RegressionAnimation(
            model=Ridge, X=X, y=y, dynamic_parameter="max_iter"
        )
        animator.ani = object()  # Simulate animation created
        animator.fig = None
        with self.assertRaises(RuntimeError):
            animator.show()

    @patch("matplotlib.pyplot.show", side_effect=Exception("show error"))
    @patch("matplotlib.pyplot.close")
    @patch("builtins.print")
    def test_show_handles_exception(self, mock_print, mock_close, mock_show):
        """Test that show() handles exceptions and closes the figure."""
        X, y = make_regression(n_samples=10, n_features=1, noise=0.1, random_state=0)
        animator = RegressionAnimation(
            model=Ridge, X=X, y=y, dynamic_parameter="max_iter"
        )
        animator.setup_plot("Test", "X", "y")
        animator.ani = object()  # Simulate animation created
        animator.show()
        mock_print.assert_any_call("Error showing animation: show error")
        mock_close.assert_called_once_with(animator.fig)
        plt.close(animator.fig)


if __name__ == "__main__":
    unittest.main()
