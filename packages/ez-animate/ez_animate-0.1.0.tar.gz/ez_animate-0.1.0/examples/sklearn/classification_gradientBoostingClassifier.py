from ez_animate import ClassificationAnimation
from sega_learn.utils import Metrics, Scaler, make_classification
from sklearn.ensemble import GradientBoostingClassifier

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
    model=GradientBoostingClassifier,
    X=X,
    y=y,
    test_size=0.25,
    dynamic_parameter="n_estimators",
    static_parameters={"learning_rate": 0.1, "max_depth": 2, "random_state": 42},
    keep_previous=True,
    metric_fn=[
        Metrics.accuracy,
        Metrics.precision,
        Metrics.recall,
    ],
)

# Set up the plot
animator.setup_plot(
    title="Gradient Boosting Classifier Animation",
    xlabel="Feature 1",
    ylabel="Feature 2",
    legend_loc="upper left",
    grid=True,
    figsize=(12, 6),
)

# Create and save the animation
n_estimators_range = range(1, 101, 5)  # Range for n_estimators parameter
animator.animate(frames=n_estimators_range, interval=150, blit=False, repeat=True)
# animator.save(
#     filename="examples/plots/sklearn_classification_gradientBoostingClassifier.gif",
#     writer="pillow",
#     fps=3,
#     dpi=300,
# )

animator.show()
