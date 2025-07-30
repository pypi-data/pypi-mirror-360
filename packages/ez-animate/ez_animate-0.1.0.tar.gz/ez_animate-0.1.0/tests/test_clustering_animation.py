import os
import sys
import unittest
import warnings

# Set OMP_NUM_THREADS=1 to avoid KMeans memory leak warning on Windows with MKL
os.environ["OMP_NUM_THREADS"] = "1"

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.utils import BaseTest, suppress_print

from ez_animate import ClusteringAnimation
from sega_learn import DBSCAN as SegaDBSCAN
from sega_learn import KMeans as SegaKMeans
from sklearn.cluster import DBSCAN, KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import accuracy_score, calinski_harabasz_score, silhouette_score


class TestClusteringAnimation(BaseTest):
    """Unit test for the ClusteringAnimation class."""

    def test_update_plot_removal_exceptions(self):
        """Test update_plot covers the except Exception: pass for cluster_centers_plot and cluster_assignments_plot removal."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.setup_plot("Test", "F1", "F2")

        # Patch cluster_centers_plot and cluster_assignments_plot to raise exception on remove
        class Dummy:
            def remove(self):
                raise Exception("remove error")

        animator.cluster_centers_plot = [Dummy()]
        animator.cluster_assignments_plot = [Dummy()]
        # Should not raise
        animator.update_plot(3)
        plt.close(animator.fig)

    def test_update_plot_colormap_fallback(self):
        """Test update_plot covers the except AttributeError for colormap fallback."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.setup_plot("Test", "F1", "F2")
        # Patch plt.colormaps.get_cmap to raise AttributeError
        orig_colormaps = getattr(plt, "colormaps", None)

        class DummyColormaps:
            def get_cmap(self, name):
                raise AttributeError()

        plt.colormaps = DummyColormaps()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            animator.update_plot(3)
        if orig_colormaps is not None:
            plt.colormaps = orig_colormaps
        plt.close(animator.fig)

    def test_update_plot_pca_transform_centers(self):
        """Test update_plot covers the PCA transform of centers (centers.shape[1] != 2)."""
        from sklearn.decomposition import PCA as SkPCA

        X = np.random.rand(100, 5)
        y = np.random.randint(0, 3, size=100)
        animator = ClusteringAnimation(
            model=KMeans,
            data=X,
            labels=y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.setup_plot("Test", "F1", "F2")
        animator.update_model(3)

        # Patch model_instance to have cluster_centers_ with shape != 2
        class DummyModel:
            def __init__(self):
                self.cluster_centers_ = np.random.rand(3, 5)

            def predict(self, X):
                return np.zeros(X.shape[0], dtype=int)

        animator.model_instance = DummyModel()
        # Patch pca_instance to a real PCA
        animator.pca_instance = SkPCA(n_components=2).fit(X)
        animator.update_plot(3)
        plt.close(animator.fig)

    def test_update_plot_no_metric_fn(self):
        """Test update_plot covers the else branch when metric_fn is None."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.setup_plot("No Metric", "F1", "F2")
        animator.update_model(3)
        artists = animator.update_plot(3)
        self.assertIsInstance(artists, tuple)
        plt.close(animator.fig)

    def test_update_plot_final_return(self):
        """Test update_plot covers the final return (no metric progression, no metric_lines)."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.setup_plot("Final Return", "F1", "F2")
        animator.update_model(4)
        # Ensure plot_metric_progression is False and metric_lines is None
        animator.plot_metric_progression = False
        if hasattr(animator, "metric_lines"):
            delattr(animator, "metric_lines")
        artists = animator.update_plot(4)
        self.assertIsInstance(artists, tuple)
        plt.close(animator.fig)

    @classmethod
    def setUpClass(cls):
        """Set up the test class (set matplotlib backend and suppress legend warnings)."""
        print("\nTesting ClusteringAnimation Class", end="", flush=True)
        mpl.use("Agg")
        # Suppress UserWarning about no artists with labels found to put in legend
        warnings.filterwarnings(
            "ignore",
            message="No artists with labels found to put in legend*",
            category=UserWarning,
        )

    def setUp(self):
        """Generate synthetic clustering data for each test."""
        self.X, self.y = make_blobs(
            n_samples=100, n_features=2, centers=3, random_state=42
        )

    def tearDown(self):
        """Cleans up after each test."""
        plt.close("all")

    def test_dummy_labels_created_when_labels_none(self):
        """Test that dummy labels are created when labels=None."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=None,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        self.assertTrue(hasattr(animator, "X_train"))
        self.assertTrue(hasattr(animator, "X_test"))
        # y_train/y_test should not exist
        self.assertFalse(hasattr(animator, "y_train"))

    def test_pca_applied_when_more_than_2_features(self):
        """Test PCA is applied when data has more than 2 features."""
        X_highdim, y_highdim = make_blobs(
            n_samples=50, n_features=5, centers=2, random_state=0
        )
        animator = ClusteringAnimation(
            model=KMeans,
            data=X_highdim,
            labels=y_highdim,
            test_size=0.2,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 2},
        )
        self.assertIsNotNone(animator.pca_instance)
        self.assertTrue(animator.needs_pca)
        self.assertEqual(animator.X_train.shape[1], 2)

    def test_error_when_less_than_2_features(self):
        """Test ValueError is raised if data has less than 2 features."""
        X_lowdim = self.X[:, :1]  # Only 1 feature
        with self.assertRaises(ValueError):
            ClusteringAnimation(
                model=KMeans,
                data=X_lowdim,
                labels=self.y,
                test_size=0.2,
                dynamic_parameter="n_init",
                static_parameters={"n_clusters": 3},
            )

    def test_setup_plot_with_true_labels_and_legend(self):
        """Test setup_plot with use_true_labels and legend enabled."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.add_legend = True
        animator.setup_plot(
            "Clustering",
            "F1",
            "F2",
            use_true_labels=True,
            legend_loc="upper right",
            grid=True,
        )
        self.assertEqual(animator.ax.get_title(), "Clustering")
        plt.close(animator.fig)

    def test_setup_plot_without_labels(self):
        """Test setup_plot when labels are None (all points gray)."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=None,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.setup_plot("No Labels", "F1", "F2")
        self.assertEqual(animator.ax.get_title(), "No Labels")
        plt.close(animator.fig)

    def test_update_model_sega_learn_fallback(self):
        """Test update_model fallback for models requiring X in constructor."""

        class DummyModel:
            def __init__(self, X=None, n_init=None, n_clusters=None):
                self.X = X
                self.n_init = n_init
                self.n_clusters = n_clusters
                self.fitted = False

            def fit(self, *args, **kwargs):
                self.fitted = True

        animator = ClusteringAnimation(
            model=DummyModel,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.update_model(5)
        self.assertTrue(hasattr(animator, "model_instance"))
        self.assertTrue(animator.model_instance.fitted)

    def test_update_plot_predict_fallback_and_warning(self):
        """Test update_plot fallback to labels_ and error if missing."""

        class NoPredictModel:
            def __init__(self, n_init=None, n_clusters=None):
                self.n_init = n_init
                self.n_clusters = n_clusters

            def fit(self, X, y=None):
                labels_ = np.zeros(100, dtype=int)  # Dummy labels
                self.labels_ = labels_

        animator = ClusteringAnimation(
            model=NoPredictModel,
            data=self.X,
            labels=None,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.setup_plot("Fallback", "F1", "F2")
        animator.update_model(1)
        # Patch labels_ to match all_data length
        all_data = np.vstack((animator.X_train, animator.X_test))
        animator.model_instance.labels_ = np.zeros(all_data.shape[0], dtype=int)
        # Should use labels_ attribute
        artists = animator.update_plot(1)
        self.assertIsInstance(artists, tuple)

        # Now test error if neither predict nor labels_
        class BadModel:
            def __init__(self, n_init=None, n_clusters=None):
                pass

            def fit(self, X, y=None):
                pass

        animator = ClusteringAnimation(
            model=BadModel,
            data=self.X,
            labels=None,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.setup_plot("Bad", "F1", "F2")
        animator.update_model(1)
        with self.assertRaises(AttributeError):
            animator.update_plot(1)

    def test_update_plot_keep_previous_and_trace_centers(self):
        """Test update_plot with keep_previous and trace_centers enabled."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
            keep_previous=True,
            trace_centers=True,
        )
        animator.setup_plot("Trace", "F1", "F2")
        # Call update_plot multiple times to build up previous_centers
        for i in range(2, 5):
            animator.update_model(i)
            artists = animator.update_plot(i)
            self.assertIsInstance(artists, tuple)
        plt.close(animator.fig)

    def test_update_plot_inconsistent_centers_warning(self):
        """Test that warning is raised if previous_centers have inconsistent shapes."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
            keep_previous=True,
            trace_centers=True,
        )
        animator.setup_plot("Warn", "F1", "F2")
        # Manually create inconsistent previous_centers
        animator.previous_centers = [np.zeros((3, 2)), np.zeros((2, 2))]
        animator.update_model(2)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            animator.update_plot(2)
            self.assertTrue(
                any("inconsistent number of centers" in str(warn.message) for warn in w)
            )
        plt.close(animator.fig)

    def test_update_plot_metric_title(self):
        """Test update_plot sets title with metric if metric_fn is provided."""
        from sklearn.metrics import silhouette_score

        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=None,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.metric_fn = [silhouette_score]
        animator.setup_plot("Metric", "F1", "F2")
        animator.update_model(3)
        _artists = animator.update_plot(3)
        self.assertIn("Silhouette_score", animator.ax.get_title())
        plt.close(animator.fig)

    def test_init(self):
        """Test ClusteringAnimation initialization with valid parameters."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
            keep_previous=True,
        )
        self.assertIsInstance(animator.X_train, np.ndarray)
        self.assertIsInstance(animator.X_test, np.ndarray)
        self.assertTrue(hasattr(animator, "unique_labels"))
        self.assertTrue(hasattr(animator, "colors"))

    def test_init_with_invalid_data(self):
        """Test initialization with invalid data input."""
        with self.assertRaises(ValueError):
            ClusteringAnimation(
                model=KMeans,
                data=None,
                labels=self.y,
                test_size=0.25,
                dynamic_parameter="n_init",
            )
        with self.assertRaises(TypeError):
            ClusteringAnimation(
                model=KMeans,
                data=list(self.X),
                labels=self.y,
                test_size=0.25,
                dynamic_parameter="n_init",
            )

    def test_init_with_invalid_labels(self):
        """Test initialization with invalid labels input."""
        with self.assertRaises(TypeError):
            ClusteringAnimation(
                model=KMeans,
                data=self.X,
                labels="not_array",
                test_size=0.25,
                dynamic_parameter="n_init",
            )

    def test_init_with_invalid_dynamic_parameter(self):
        """Test initialization with invalid dynamic_parameter input."""
        with self.assertRaises(ValueError):
            ClusteringAnimation(
                model=KMeans,
                data=self.X,
                labels=self.y,
                test_size=0.25,
                dynamic_parameter=0,
            )

    def test_init_with_invalid_static_parameters(self):
        """Test initialization with invalid static_parameters input."""
        with self.assertRaises(ValueError):
            ClusteringAnimation(
                model=KMeans,
                data=self.X,
                labels=self.y,
                test_size=0.25,
                dynamic_parameter="n_init",
                static_parameters=["invalid_param"],
            )

    def test_init_with_invalid_keep_previous(self):
        """Test initialization with invalid keep_previous input."""
        with self.assertRaises(ValueError):
            ClusteringAnimation(
                model=KMeans,
                data=self.X,
                labels=self.y,
                test_size=0.25,
                dynamic_parameter="n_init",
                keep_previous="invalid_value",
            )

    def test_init_with_invalid_pca_components(self):
        """Test initialization with invalid pca_components input."""
        with self.assertRaises(ValueError):
            ClusteringAnimation(
                model=KMeans,
                data=self.X,
                labels=self.y,
                test_size=0.25,
                dynamic_parameter="n_init",
                pca_components=0,
            )

    def test_init_with_invalid_trace_centers(self):
        """Test initialization with invalid trace_centers input."""
        with self.assertRaises(ValueError):
            ClusteringAnimation(
                model=KMeans,
                data=self.X,
                labels=self.y,
                test_size=0.25,
                dynamic_parameter="n_init",
                trace_centers="invalid_value",
            )

    def test_init_with_scaler(self):
        """Test initialization with a scaler."""
        from sega_learn import Scaler

        scaler = Scaler()
        with suppress_print():
            animator = ClusteringAnimation(
                model=KMeans,
                data=self.X,
                labels=self.y,
                test_size=0.25,
                dynamic_parameter="n_init",
                static_parameters={"n_clusters": 3},
                scaler=scaler,
            )
        self.assertIsInstance(animator.scaler_instance, Scaler)

    def test_pca_components_more_than_2(self):
        """Test initialization with pca_components > 2."""
        # data.shape[1] > 2:
        X = np.random.rand(100, 5)  # 5 features
        y = np.random.randint(0, 3, size=100)
        with suppress_print():
            animation = ClusteringAnimation(
                model=KMeans,
                data=X,
                labels=y,
                test_size=0.25,
                dynamic_parameter="n_init",
                pca_components=3,
            )
        self.assertEqual(animation.pca_instance.n_components, 2)

    def test_setup_plot(self):
        """Test setup_plot with valid parameters."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        animator.setup_plot("Test Clustering", "Feature 1", "Feature 2")
        self.assertIsNotNone(animator.fig)
        self.assertIsNotNone(animator.ax)
        self.assertEqual(animator.ax.get_title(), "Test Clustering")
        plt.close(animator.fig)

    def test_update_model_sklearn(self):
        """Test update_model with valid frame parameter."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        with suppress_print():
            animator.update_model(10)
        self.assertIsInstance(animator.model_instance, KMeans)
        self.assertEqual(animator.model_instance.n_init, 10)
        self.assertEqual(animator.model_instance.n_clusters, 3)

    def test_update_model_sklearn_2(self):
        """Test update_model with valid frame parameter, DBSCAN model."""
        animator = ClusteringAnimation(
            model=DBSCAN,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="eps",
            static_parameters={"min_samples": 5},
        )
        with suppress_print():
            animator.update_model(0.5)
        self.assertIsInstance(animator.model_instance, DBSCAN)
        self.assertEqual(animator.model_instance.eps, 0.5)
        self.assertEqual(animator.model_instance.min_samples, 5)

    def test_update_model_pca(self):
        """Test update_model with PCA applied."""
        X_highdim, y_highdim = make_blobs(
            n_samples=100, n_features=5, centers=3, random_state=42
        )
        animator = ClusteringAnimation(
            model=KMeans,
            data=X_highdim,
            labels=y_highdim,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        with suppress_print():
            animator.update_model(10)
        self.assertIsInstance(animator.model_instance, KMeans)
        self.assertEqual(animator.model_instance.n_init, 10)
        self.assertEqual(animator.model_instance.n_clusters, 3)

    def test_update_model_sega_learn(self):
        """Test update_model with sega_learn model."""
        animator = ClusteringAnimation(
            model=SegaKMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="max_iter",
            static_parameters={"n_clusters": 3},
        )
        with suppress_print():
            animator.update_model(10)
        self.assertIsInstance(animator.model_instance, SegaKMeans)
        self.assertEqual(animator.model_instance.max_iter, 10)
        self.assertEqual(animator.model_instance.n_clusters, 3)

    def test_update_model_sega_learn_2(self):
        """Test update_model with sega_learn DBSCAN model."""
        animator = ClusteringAnimation(
            model=SegaDBSCAN,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="eps",
            static_parameters={"min_samples": 5},
        )
        with suppress_print():
            animator.update_model(0.5)
        self.assertIsInstance(animator.model_instance, SegaDBSCAN)
        self.assertEqual(animator.model_instance.eps, 0.5)
        self.assertEqual(animator.model_instance.min_samples, 5)

    def test_update_plot(self):
        """Test update_plot with valid parameters and labels."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        with suppress_print():
            animator.setup_plot("Test Clustering", "Feature 1", "Feature 2")
            animator.update_model(10)
            artists = animator.update_plot(10)
        self.assertIsInstance(artists, tuple)
        self.assertGreaterEqual(len(artists), 1)
        plt.close(animator.fig)

    def test_update_plot_no_labels(self):
        """Test update_plot with no labels provided."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=None,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
        )
        with suppress_print():
            animator.setup_plot("Test Clustering", "Feature 1", "Feature 2")
            animator.update_model(10)
            artists = animator.update_plot(10)
        self.assertIsInstance(artists, tuple)
        self.assertGreaterEqual(len(artists), 1)
        plt.close(animator.fig)

    def test_update_plot_with_trace_centers(self):
        """Test update_plot with trace_centers enabled."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
            trace_centers=True,
        )
        with suppress_print():
            animator.setup_plot("Test Clustering", "Feature 1", "Feature 2")
            animator.update_model(10)
            artists = animator.update_plot(10)
        self.assertIsInstance(artists, tuple)
        self.assertGreaterEqual(len(artists), 1)
        plt.close(animator.fig)

    def test_update_plot_with_non_clustering_metric(self):
        """Test update_plot with a non-clustering metric."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
            metric_fn=accuracy_score,
        )
        with suppress_print():
            animator.setup_plot("Test Clustering", "Feature 1", "Feature 2")
            animator.update_model(10)
            artists = animator.update_plot(10)
        self.assertIsInstance(artists, tuple)
        self.assertGreaterEqual(len(artists), 1)
        plt.close(animator.fig)

    def test_update_plot_with_multiple_metrics(self):
        """Test update_plot with multiple metrics."""
        animator = ClusteringAnimation(
            model=KMeans,
            data=self.X,
            labels=self.y,
            test_size=0.25,
            dynamic_parameter="n_init",
            static_parameters={"n_clusters": 3},
            metric_fn=[silhouette_score, calinski_harabasz_score, accuracy_score],
        )
        with suppress_print():
            animator.setup_plot("Test Clustering", "Feature 1", "Feature 2")
            animator.update_model(10)
            artists = animator.update_plot(10)
        self.assertIsInstance(artists, tuple)
        self.assertGreaterEqual(len(artists), 1)
        plt.close(animator.fig)


if __name__ == "__main__":
    unittest.main()
