import warnings

from ez_animate import ClusteringAnimation
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import calinski_harabasz_score, silhouette_score

# Suppress warnings for cleaner output (KMeans)
warnings.filterwarnings("ignore")

# Generate a synthetic dataset for clustering
X, y = make_blobs(
    n_samples=1000,
    n_features=2,
    centers=6,
    center_box=(-7.5, 7.5),
    cluster_std=0.8,
    random_state=1,
)

# Create the animation using ClusteringAnimation
animator = ClusteringAnimation(
    model=KMeans,
    data=X,
    labels=y,
    dynamic_parameter="max_iter",
    static_parameters={
        "n_clusters": 4,
        "init": "random",
        "n_init": 1,
        "random_state": 42,
    },
    keep_previous=True,
    trace_centers=True,
    metric_fn=[silhouette_score, calinski_harabasz_score],
    plot_metric_progression=True,
    max_metric_subplots=2,
)

# Set up the plot
animator.setup_plot(
    title="K-Means Clustering Animation",
    xlabel="Feature 1",
    ylabel="Feature 2",
    legend_loc="upper right",
    grid=True,
    figsize=(10, 6),
)

# Animate over a range of iterations
max_iters = 15
animator.animate(frames=range(1, max_iters + 1), interval=500, blit=False, repeat=False)

# To save the animation, uncomment the following lines:
# animator.save(
#     filename="examples/plots/sklearn_clustering_kmeans_traced.gif",
#     writer="pillow",
#     fps=2,
#     dpi=150,
# )

animator.show()
