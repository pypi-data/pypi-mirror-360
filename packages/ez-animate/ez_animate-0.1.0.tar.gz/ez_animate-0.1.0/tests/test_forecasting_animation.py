import os
import sys
import unittest

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.utils import BaseTest, suppress_print

from ez_animate import (
    ForecastingAnimation,
)
from sega_learn.time_series.moving_average import ExponentialMovingAverage
from sega_learn.utils import (
    Metrics,
    make_time_series,
)


class MockModelNoFit:
    """Mock model that does not implement fit method."""

    def __init__(self, **kwargs):  # noqa: D107
        self.params = kwargs

    def predict(self, X):  # noqa: D102
        return X


class MockModelBadFit:
    """Mock model that raises an error on fit."""

    def __init__(self, **kwargs):  # noqa: D107
        self.params = kwargs

    def predict(self, X):  # noqa: D102
        return X

    def fit(self, X, y):  # noqa: D102
        raise ValueError("This model does not support fitting.")


class MockModelNoPredict:
    """Mock model that does not implement predict method."""

    def __init__(self, **kwargs):  # noqa: D107
        self.params = kwargs

    def fit(self, X, y):  # noqa: D102
        pass


class MockModelBadPredict:
    """Mock model that raises an error on predict."""

    def __init__(self, **kwargs):  # noqa: D107
        self.params = kwargs

    def fit(self, X, y):  # noqa: D102
        pass

    def predict(self, X):  # noqa: D102
        raise ValueError("This model does not support prediction.")


class MockPredictor:
    """Mock predictor returns values as pandas DataFrame."""

    def __init__(self, **kwargs):  # noqa: D107
        self.params = kwargs

    def fit(self, X, y):  # noqa: D102
        return self

    def predict(self, X):  # noqa: D102
        return pd.DataFrame(X)

    def forecast(self, steps):  # noqa: D102
        return pd.DataFrame(
            [[i + 1 for i in range(steps)]],
            columns=[f"feature_{i}" for i in range(steps)],
        )


class TestforecastingAnimation(BaseTest):
    """Unit test for the forecastingAnimation class."""

    @classmethod
    def setUpClass(cls):  # NOQA D201
        """Initializes the test suite."""
        print("\nTesting forecastingAnimation Class", end="", flush=True)
        mpl.use("Agg")

    def setUp(self):  # NOQA D201
        """Prepares each test."""
        # Generate a synthetic time series
        self.time_series = make_time_series(
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
        train_size = int(len(self.time_series) * 0.8)
        self.train_series = self.time_series[:train_size]
        self.test_series = self.time_series[train_size:]
        self.forecast_steps = len(self.test_series)

    def test_init(self):
        """Test forecastingAnimation initialization."""
        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
            keep_previous=True,
        )
        self.assertEqual(animator.forecast_steps, self.forecast_steps)
        self.assertEqual(len(animator.train_indices), len(self.train_series))
        self.assertEqual(len(animator.forecast_indices), self.forecast_steps)
        self.assertTrue(hasattr(animator, "previous_forecast_lines"))
        self.assertTrue(hasattr(animator, "previous_fitted_lines"))

    def test_init_no_dynamic_parameter(self):
        """Test initialization with no dynamic parameter."""
        with self.assertRaises(ValueError):
            ForecastingAnimation(
                model=ExponentialMovingAverage,
                train_series=self.train_series,
                test_series=self.test_series,
                forecast_steps=self.forecast_steps,
                dynamic_parameter=None,
                keep_previous=True,
            )

    def test_init_no_static_parameters(self):
        """Test initialization with no static parameters."""
        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
            static_parameters=None,
            keep_previous=True,
        )
        self.assertIsNotNone(animator)
        self.assertDictEqual(animator.static_parameters, {})

    def test_init_invalid_static_parameters(self):
        """Test initialization with invalid static parameters."""
        with self.assertRaises(ValueError):
            ForecastingAnimation(
                model=ExponentialMovingAverage,
                train_series=self.train_series,
                test_series=self.test_series,
                forecast_steps=self.forecast_steps,
                dynamic_parameter="alpha",
                static_parameters=["invalid_param", 0.5],
                keep_previous=True,
            )

    def test_init_invalid_keep_previous(self):
        """Test initialization with invalid keep_previous parameter."""
        with self.assertRaises(ValueError):
            ForecastingAnimation(
                model=ExponentialMovingAverage,
                train_series=self.train_series,
                test_series=self.test_series,
                forecast_steps=self.forecast_steps,
                dynamic_parameter="alpha",
                keep_previous="invalid_value",
            )

    def test_init_no_train_series(self):
        """Test initialization with no train series."""
        with self.assertRaises(ValueError):
            ForecastingAnimation(
                model=ExponentialMovingAverage,
                train_series=None,
                test_series=self.test_series,
                forecast_steps=self.forecast_steps,
                dynamic_parameter="alpha",
                keep_previous=True,
            )

    def test_metric_to_list(self):
        """Test metric_to_list with valid metrics."""
        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
            metric_fn=Metrics.mean_squared_error,
        )
        metrics_list = animator.metric_fn
        self.assertIsInstance(metrics_list, list)
        self.assertEqual(len(metrics_list), 1)
        self.assertEqual(metrics_list[0], Metrics.mean_squared_error)

    def test_setup_plot(self):
        """Test setup_plot with valid parameters."""
        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
        )
        animator.setup_plot("Test Forecasting", "Time", "Value")
        self.assertIsNotNone(animator.fig)
        self.assertIsNotNone(animator.ax)
        self.assertEqual(animator.ax.get_title(), "Test Forecasting")
        self.assertIsNotNone(animator.fitted_line)
        self.assertIsNotNone(animator.forecast_line)
        plt.close(animator.fig)

    def test_setup_plot_no_legend(self):
        """Test setup_plot with no legend."""
        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
            show_legend=False,
        )
        animator.setup_plot("Test Forecasting", "Time", "Value", legend_loc=None)
        self.assertIsNotNone(animator.fig)
        self.assertIsNotNone(animator.ax)
        self.assertEqual(animator.ax.get_title(), "Test Forecasting")
        self.assertIsNotNone(animator.fitted_line)
        self.assertIsNotNone(animator.forecast_line)
        plt.close(animator.fig)

    def test_update_model(self):
        """Test update_model with valid frame parameter."""
        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
        )
        with suppress_print():
            # Test with a specific alpha value
            animator.update_model(0.3)
        self.assertIsInstance(animator.model_instance, ExponentialMovingAverage)
        self.assertEqual(animator.model_instance.alpha, 0.3)
        self.assertEqual(len(animator.fitted_values), len(self.train_series))
        self.assertEqual(len(animator.forecast_values), self.forecast_steps)

    def test_update_model_no_fit(self):
        """Test update_model with a model that does not implement fit."""
        animator = ForecastingAnimation(
            model=MockModelNoFit,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
        )
        with self.assertRaises(AttributeError):
            animator.update_model(0.3)

    def test_update_model_bad_fit(self):
        """Test update_model with a model that raises an error on fit."""
        animator = ForecastingAnimation(
            model=MockModelBadFit,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
        )
        with self.assertRaises(TypeError):
            animator.update_model(0.3)

    def test_update_model_bad_predict(self):
        """Test update_model with a model that raises an error on predict."""
        animator = ForecastingAnimation(
            model=MockModelBadPredict,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
        )
        # Should NOT raise an error here
        animator.update_model(0.3)

    def test_update_model_no_predict(self):
        """Test update_model with a model that does not implement predict."""
        animator = ForecastingAnimation(
            model=MockModelNoPredict,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
        )
        with self.assertRaises(AttributeError):
            animator.update_model(0.3)

    def test_update_model_pandas_predictor(self):
        """Test update_model with a pandas DataFrame predictor."""
        animator = ForecastingAnimation(
            model=MockPredictor,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
        )
        with suppress_print():
            animator.update_model(0.3)

    def test_update_plot_with_metrics(self):
        """Test update_plot with metrics."""
        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
            metric_fn=[Metrics.mean_squared_error],
        )
        with suppress_print():
            animator.setup_plot("Test Forecasting", "Time", "Value")
            animator.update_model(0.3)

            # Check that update_plot returns a list of artists
            artists = animator.update_plot(0.3)

        self.assertIsInstance(artists, list)
        self.assertTrue(all(isinstance(artist, plt.Line2D) for artist in artists))
        plt.close(animator.fig)

    def test_update_plot_keep_previous(self):
        """Test update_plot with keep_previous=True."""
        animator = ForecastingAnimation(
            model=ExponentialMovingAverage,
            train_series=self.train_series,
            test_series=self.test_series,
            forecast_steps=self.forecast_steps,
            dynamic_parameter="alpha",
            keep_previous=True,
            max_previous=1,
        )
        with suppress_print():
            animator.setup_plot("Test Forecasting", "Time", "Value")
            animator.update_model(0.3)

            # Check that update_plot returns a list of artists
            artists = animator.update_plot(0.3)

        self.assertIsInstance(artists, list)
        self.assertTrue(all(isinstance(artist, plt.Line2D) for artist in artists))
        plt.close(animator.fig)


if __name__ == "__main__":
    unittest.main()
