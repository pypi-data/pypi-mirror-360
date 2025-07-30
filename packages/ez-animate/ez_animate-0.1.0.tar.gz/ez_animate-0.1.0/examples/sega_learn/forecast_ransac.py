from ez_animate import ForecastingAnimation
from sega_learn.linear_models import RANSAC
from sega_learn.utils import Metrics, make_time_series

# Generate a synthetic time series
time_series = make_time_series(
    n_samples=1,
    n_timestamps=300,
    n_features=1,
    trend="linear",
    seasonality="sine",
    seasonality_period=60,
    noise=0.25,
    random_state=1,
)

# Flatten the time series to 1D if it's not already
time_series = time_series.flatten()

# Split into training and testing sets
train_size = int(len(time_series) * 0.7)
train_series, test_series = time_series[:train_size], time_series[train_size:]
forecast_steps = len(test_series)

# Create the animation using forecastingAnimation
animator = ForecastingAnimation(
    model=RANSAC,
    train_series=train_series,
    test_series=test_series,
    forecast_steps=forecast_steps,
    keep_previous=True,
    dynamic_parameter="n",
    # static_parameters={"alpha": 1.0, "fit_intercept": True},
    metric_fn=[
        Metrics.mean_squared_error,
        Metrics.mean_absolute_error,
    ],
)

# Set up the plot
animator.setup_plot(
    title="RANSAC Regression Forecast",
    xlabel="Time Step",
    ylabel="Value",
    legend_loc="upper left",
    grid=True,
    figsize=(12, 6),
)

# Create and save the animation
n_range = range(10, 111, 1)
animator.animate(frames=n_range, interval=150, blit=False, repeat=True)
# animator.save(
#     filename="examples/plots/sega_learn_forecast_ransac.gif",
#     writer="pillow",
#     fps=5,
#     dpi=300,
# )

# To show the animation
animator.show()
