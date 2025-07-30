import warnings

import numpy as np

from ez_animate import ClassificationAnimation
from sega_learn.utils import Metrics, Scaler, make_classification
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import f1_score

# Suppress warnings from sklearn about convergence
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")


def macro_f1_score(y_true, y_pred):
    """Calculate macro F1 score."""
    return f1_score(y_true, y_pred, average="macro")


# Generate a binary classification dataset
X, y = make_classification(
    n_samples=300,
    n_features=2,
    n_redundant=0,
    n_informative=2,
    n_classes=3,
    random_state=42,
    n_clusters_per_class=1,
    class_sep=1,
)

# Scaleer for features
scaler = Scaler()

# Create the animation using RegressionAnimation
animator = ClassificationAnimation(
    model=SGDClassifier,
    X=X,
    y=y,
    test_size=0.25,
    dynamic_parameter="max_iter",
    static_parameters={
        "fit_intercept": True,
        "tol": 1e-3,
        "learning_rate": "constant",
        "eta0": 0.005,
    },
    keep_previous=True,
    metric_fn=[
        macro_f1_score,
        Metrics.precision,
        Metrics.recall,
    ],
    plot_metric_progression=True,
    max_metric_subplots=2,
)

# Set up the plot
animator.setup_plot(
    title="SGD Classifier Animation",
    xlabel="Feature 1",
    ylabel="Feature 2",
    legend_loc="upper left",
    grid=True,
    figsize=(12, 6),
)

# Create and save the animation
iter_range = np.arange(1, 101, 1)
animator.animate(frames=iter_range, interval=150, blit=False, repeat=True)
# animator.save(
#     filename="examples/plots/sklearn_classification_sgd.gif",
#     writer="pillow",
#     fps=3,
#     dpi=300,
# )

animator.show()
