# Usage

`ez-animate` is compatible with both Scikit-learn and sega_learn models, making it a versatile tool for creating animations of machine learning model behavior. See below for examples of how to use `ez-animate` with different types of models. Or see [API Reference](api.md) for more details on available methods and customization options.

More advanced usage examples can be found in the on [GitHub](https://github.com/SantiagoEnriqueGA/ez-animate/tree/master/examples).


## Complete Scikit-learn Example

This section demonstrates how to use `ez-animate` with a Scikit-learn SGD regression model to create an animation of the model's predictions for max_iter values ranging from 1 to 100.

```python
import numpy as np

from ez_animate import RegressionAnimation
from sega_learn.utils import Metrics, make_regression
from sklearn.linear_model import SGDRegressor

# Generate synthetic regression data
X, y = make_regression(n_samples=1000, n_features=1)

# Create the animation using RegressionAnimation
animator = RegressionAnimation(
    model=SGDRegressor,
    X=X,
    y=y,
    test_size=0.25,
    dynamic_parameter="max_iter",
    static_parameters={"fit_intercept": True, "eta0": 0.0005},
    keep_previous=True,
    max_previous=25,
    metric_fn=[
        Metrics.r_squared,
        Metrics.mean_squared_error,
    ],
    plot_metric_progression=True,
    max_metric_subplots=2,
)

# Set up the plot
animator.setup_plot(
    title="SGD Regression Animation",
    xlabel="Feature Coefficient",
    ylabel="Target Value",
    legend_loc="upper left",
    grid=True,
    figsize=(14, 6),
)

# Create and save the animation
iter_range = np.arange(1, 100, 1)
animator.animate(frames=iter_range, interval=150, blit=False, repeat=True)
animator.show()

```
![SGD Regression Animation](plots/animator_sgd.gif)


## Complete sega_learn Example

This section demonstrates how to use `ez-animate` with a time series forecasting model from `sega_learn` to animate the effect of the `alpha` parameter in Exponential Moving Average forecasting.

```python
import numpy as np

from ez_animate import ForecastingAnimation
from sega_learn.time_series.moving_average import ExponentialMovingAverage
from sega_learn.utils import Metrics, make_time_series

# Generate a synthetic time series
time_series = make_time_series(
    n_samples=1,
    n_timestamps=300,
    n_features=1,
    trend="linear",
    seasonality="sine",
    seasonality_period=30,
    noise=0.1,
    random_state=1,
)

# Flatten the time series to 1D if it's not already
time_series = time_series.flatten()

# Split into training and testing sets
train_size = int(len(time_series) * 0.8)
train_series, test_series = time_series[:train_size], time_series[train_size:]
forecast_steps = len(test_series)

# Create the animation using ForecastingAnimation
animator = ForecastingAnimation(
    model=ExponentialMovingAverage,
    train_series=train_series,
    test_series=test_series,
    forecast_steps=forecast_steps,
    keep_previous=True,
    dynamic_parameter="alpha",
    metric_fn=[
        Metrics.mean_squared_error,
        Metrics.mean_absolute_error,
    ],
)

# Set up the plot
animator.setup_plot(
    title="Exponential Moving Average Forecast",
    xlabel="Time Step",
    ylabel="Value",
    legend_loc="upper left",
    grid=True,
    figsize=(12, 6),
)

# Create and show the animation
alpha_range = np.arange(0.01, 0.5, 0.01)
animator.animate(frames=alpha_range, interval=150, blit=True, repeat=False)
animator.show()
```
![Exponential Moving Average Forecast Animation](plots/animator_ema_forecast.gif)


## Specific Features

This section highlights some of the key features of `ez-animate` and how to use them with the `AnimationBase` class and its subclasses.

### Customizing Figures and Axes

You can customize the plot's title, axis labels, grid, legend location, and figure size using the `setup_plot` method:

```python
animator.setup_plot(
    title="Custom Animation Title",
    xlabel="X Axis Label",
    ylabel="Y Axis Label",
    legend_loc="upper right",
    grid=True,
    figsize=(10, 5),
)
```

### Saving Animations

After creating an animation, you can save it as a GIF or MP4 using the `save` method:

```python
animator.save(
    filename="my_animation.gif",  # or "my_animation.mp4"
    writer="pillow",              # or "ffmpeg" for MP4
    fps=10,
    dpi=150,
)
```

### Controlling Animation Speed and Playback

You can control the speed of the animation using the `interval` parameter in the `animate` method (milliseconds between frames), and set whether the animation repeats:

```python
animator.animate(frames=range(1, 100), interval=100, blit=True, repeat=False)
```

### Additional Notes

- The `AnimationBase` class is designed for extensibility. Subclasses like `RegressionAnimation`, `ClassificationAnimation`, and `ForecastingAnimation` implement model-specific logic.
- You can pass additional keyword arguments to customize plot elements or metrics.
- The `show()` method displays the animation in a Matplotlib window.

See [API Reference](api.md) for more details on available methods and customization options.
