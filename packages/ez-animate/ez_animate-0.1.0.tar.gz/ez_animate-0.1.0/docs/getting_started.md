# Getting Started

## Installation

> **Note:** PyPI release is pending. For now, install directly from GitHub.

```bash
pip install ez-animate
```

Or, for development:

```bash
git clone https://github.com/SantiagoEnriqueGA/ez-animate.git
cd ez-animate
uv venv
.venv\Scripts\Activate.ps1  # On Windows PowerShell
.venv\Scripts\activate.bat    # On Windows CMD
source .venv/bin/activate   # On macOS/Linux
uv pip install -e .[test,lint,docs]
```

## Quickstart

```python
from ez_animate import RegressionAnimation

# Create and run the animation
animator = RegressionAnimation(
    model=Lasso,    # Scikit-learn or sega_learn model class
    X=X,
    y=y,
    test_size=0.25,
    dynamic_parameter="alpha",
    static_parameters={"max_iter": 1, "fit_intercept": True},
    keep_previous=True,
    metric_fn=Metrics.mean_squared_error,
)

# Set up the plot
animator.setup_plot(
    title="Regression Animation",
    xlabel="Feature Coefficient",
    ylabel="Target Value",
)

# Create the animation
animator.animate(frames=np.arange(0.01, 1.0, 0.01))

# Show and save the animation
animator.show()
animator.save("regression_animation.gif")
```

See [Usage](usage.md) for more details.
