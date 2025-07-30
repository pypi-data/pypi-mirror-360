import warnings

import numpy as np

from ez_animate import RegressionAnimation
from sega_learn.utils import Metrics, make_regression
from sklearn.linear_model import SGDRegressor

# Suppress warnings from sklearn about convergence
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# Generate synthetic regression data
X, y = make_regression(
    n_samples=1000,
    n_features=1,
    noise=1.25,
    random_state=42,
    tail_strength=10,
    bias=0.5,
)


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
        Metrics.mean_absolute_error,
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
# animator.save(
#     filename="examples/plots/sklearn_regression_sgd.gif",
#     writer="pillow",
#     fps=10,
#     dpi=300,
# )

animator.show()
