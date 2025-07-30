import numpy as np

from ez_animate import RegressionAnimation
from sega_learn.utils import Metrics, make_regression
from sklearn.linear_model import Lasso

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
    model=Lasso,
    X=X,
    y=y,
    test_size=0.25,
    dynamic_parameter="alpha",
    static_parameters={"max_iter": 1, "fit_intercept": True},
    keep_previous=True,
    metric_fn=[
        Metrics.mean_squared_error,
        Metrics.mean_absolute_error,
        Metrics.r_squared,
    ],
)

# Set up the plot
animator.setup_plot(
    title="Lasso Regression Animation",
    xlabel="Feature Coefficient",
    ylabel="Target Value",
    legend_loc="upper left",
    grid=True,
    figsize=(12, 6),
)

# Create and save the animation
alpha_range = np.arange(0.01, 1.0, 0.01)
animator.animate(frames=alpha_range, interval=150, blit=False, repeat=True)
# animator.save(
#     filename="examples/plots/sklearn_regression_lasso.gif",
#     writer="pillow",
#     fps=10,
#     dpi=300,
# )

animator.show()
