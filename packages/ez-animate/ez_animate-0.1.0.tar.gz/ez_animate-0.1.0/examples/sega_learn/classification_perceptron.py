from ez_animate import ClassificationAnimation
from sega_learn.linear_models import Perceptron
from sega_learn.utils import Metrics, Scaler, make_classification

# Generate a binary classification dataset
X, y = make_classification(
    n_samples=300,
    n_features=2,
    n_redundant=0,
    n_informative=2,
    n_classes=2,
    random_state=42,
    n_clusters_per_class=1,
    class_sep=1,
)

# Scaleer for features
scaler = Scaler()

# Create the animation using RegressionAnimation
animator = ClassificationAnimation(
    model=Perceptron,
    X=X,
    y=y,
    test_size=0.25,
    dynamic_parameter="max_iter",
    static_parameters={"learning_rate": 0.001},
    keep_previous=True,
    scaler=scaler,
    metric_fn=[
        Metrics.accuracy,
        Metrics.precision,
        Metrics.recall,
    ],
)

# Set up the plot
animator.setup_plot(
    title="Perceptron Animation",
    xlabel="Feature 1",
    ylabel="Feature 2",
    legend_loc="upper left",
    grid=True,
    figsize=(12, 6),
)

# Create and save the animation
max_iter_range = range(1, 2500, 100)
animator.animate(frames=max_iter_range, interval=150, blit=False, repeat=True)
# animator.save(
#     filename="examples/plots/sega_learn_classification_perceptron.gif",
#     writer="pillow",
#     fps=3,
#     dpi=300,
# )

animator.show()
