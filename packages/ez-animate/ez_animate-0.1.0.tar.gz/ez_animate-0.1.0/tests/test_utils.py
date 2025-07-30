import os
import sys
import unittest

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tests.utils import BaseTest

from ez_animate import PCA
from ez_animate.utils import train_test_split


class TestPCA(BaseTest):
    """Unit tests for the PCA class."""

    @classmethod
    def setUpClass(cls):  # NOQA D201
        print("\nTesting PCA", end="", flush=True)

    def setUp(self):  # NOQA D201
        """Set up the PCA instance for testing."""
        self.X = np.random.rand(100, 5)

    def test_pca_fit_transform(self):
        """Tests the fit_transform method of the PCA class."""
        pca = PCA(n_components=2)
        X_transformed = pca.fit_transform(self.X)
        self.assertEqual(X_transformed.shape[1], 2)
        self.assertEqual(pca.get_components().shape[1], 2)

    def test_pca_fit_invalid_input_string(self):
        """Test PCA.fit with a string input."""
        pca = PCA(n_components=2)
        with self.assertRaises(ValueError):
            pca.fit("invalid_input")

    def test_pca_fit_invalid_input_1d(self):
        """Test PCA.fit with 1D array input."""
        pca = PCA(n_components=2)
        with self.assertRaises(ValueError):
            pca.fit(np.random.rand(100))

    def test_pca_fit_invalid_input_single_feature(self):
        """Test PCA.fit with single feature input."""
        pca = PCA(n_components=2)
        with self.assertRaises(ValueError):
            pca.fit(np.random.rand(100, 1))

    def test_pca_transform_invalid_input_string(self):
        """Test PCA.transform with a string input."""
        pca = PCA(n_components=2)
        with self.assertRaises(ValueError):
            pca.transform("invalid_input")

    def test_pca_transform_invalid_input_1d(self):
        """Test PCA.transform with 1D array input."""
        pca = PCA(n_components=2)
        with self.assertRaises(ValueError):
            pca.transform(np.random.rand(100))

    def test_pca_transform_invalid_input_shape(self):
        """Tests Input data must have the same number of features as the data used to fit the model."""
        pca = PCA(n_components=2)
        pca.fit(self.X)
        with self.assertRaises(ValueError):
            pca.transform(np.random.rand(100, 3))

    def test_pca_inverse_transform(self):
        """Test PCA.inverse_transform."""
        pca = PCA(n_components=2)
        pca.fit(self.X)
        X_transformed = pca.transform(self.X)
        X_inverse_transformed = pca.inverse_transform(X_transformed)
        self.assertEqual(X_inverse_transformed.shape, self.X.shape)

    def test_pca_inverse_transform_invalid_input_string(self):
        """Test PCA.inverse_transform with a string input."""
        pca = PCA(n_components=2)
        with self.assertRaises(ValueError):
            pca.inverse_transform("invalid_input")

    def test_pca_inverse_transform_invalid_input_1d(self):
        """Test PCA.inverse_transform with 1D array input."""
        pca = PCA(n_components=2)
        with self.assertRaises(ValueError):
            pca.inverse_transform(np.random.rand(100))

    def test_get_explained_variance_ratio(self):
        """Test PCA.get_explained_variance_ratio."""
        pca = PCA(n_components=2)
        pca.fit(self.X)
        explained_variance_ratio = pca.get_explained_variance_ratio()
        self.assertEqual(len(explained_variance_ratio), 2)


class TestFuncs(BaseTest):
    """Unit tests for the utility functions."""

    @classmethod
    def setUpClass(cls):  # NOQA D201
        print("\nTesting Utility Functions", end="", flush=True)

    def setUp(self):  # NOQA D201
        """Set up the utility functions for testing."""

    def test_basic_split_default(self):
        """Test basic split with default parameters."""
        X = np.arange(20).reshape(10, 2)
        y = np.arange(10)
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
        self.assertEqual(X_train.shape[0] + X_test.shape[0], 10)
        self.assertEqual(len(y_train) + len(y_test), 10)
        self.assertEqual(X_train.shape[1], 2)
        self.assertEqual(X_test.shape[1], 2)

    def test_split_with_float_sizes(self):
        """Test split with float test_size."""
        X = np.arange(40).reshape(20, 2)
        y = np.arange(20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=0
        )
        self.assertEqual(X_test.shape[0], 6)
        self.assertEqual(X_train.shape[0], 14)

    def test_split_with_int_sizes(self):
        """Test split with integer test_size."""
        X = np.arange(30).reshape(10, 3)
        y = np.arange(10)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=3, random_state=1
        )
        self.assertEqual(X_test.shape[0], 3)
        self.assertEqual(X_train.shape[0], 7)

    def test_split_with_train_size(self):
        """Test split with float train_size."""
        X = np.arange(50).reshape(10, 5)
        y = np.arange(10)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_size=0.6, random_state=2
        )
        self.assertEqual(X_train.shape[0], 6)
        self.assertEqual(X_test.shape[0], 4)

    def test_split_with_both_sizes(self):
        """Test split with both train_size and test_size as integers."""
        X = np.arange(60).reshape(12, 5)
        y = np.arange(12)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_size=5, test_size=5, random_state=3
        )
        self.assertEqual(X_train.shape[0], 5)
        self.assertEqual(X_test.shape[0], 5)

    def test_split_no_shuffle(self):
        """Test split with shuffle=False."""
        X = np.arange(20).reshape(10, 2)
        y = np.arange(10)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, shuffle=False, test_size=0.2
        )
        self.assertTrue(np.all(X_train == X[:8]))
        self.assertTrue(np.all(X_test == X[8:]))

    def test_split_stratify(self):
        """Test stratified split."""
        X = np.arange(40).reshape(20, 2)
        y = np.array([0] * 10 + [1] * 10)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.5, stratify=y, random_state=0
        )
        self.assertEqual(sum(y_train), 5)
        self.assertEqual(sum(y_test), 5)
        self.assertEqual(len(y_train), 10)
        self.assertEqual(len(y_test), 10)

    def test_split_stratify_invalid(self):
        """Test stratify with only one class raises ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.array([0, 0, 0, 0, 0])
        with self.assertRaises(ValueError):
            train_test_split(X, y, stratify=y)

    def test_split_invalid_sizes(self):
        """Test invalid test_size and train_size values raise ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(5)
        with self.assertRaises(ValueError):
            train_test_split(X, y, test_size=1.5)
        with self.assertRaises(ValueError):
            train_test_split(X, y, train_size=6)
        with self.assertRaises(ValueError):
            train_test_split(X, y, train_size=3, test_size=3)

    def test_split_mismatched_lengths(self):
        """Test arrays of different lengths raise ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(6)
        with self.assertRaises(ValueError):
            train_test_split(X, y)

    def test_split_list_input(self):
        """Test splitting lists as input."""
        X = list(range(10))
        y = list(range(10))
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=0
        )
        self.assertEqual(len(X_train) + len(X_test), 10)
        self.assertIsInstance(X_train, list)
        self.assertIsInstance(X_test, list)

    def test_split_sparse_input(self):
        """Test splitting sparse matrix as input."""
        X = csr_matrix(np.arange(20).reshape(10, 2))
        y = np.arange(10)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=0
        )
        self.assertEqual(X_train.shape[0] + X_test.shape[0], 10)
        self.assertEqual(X_train.shape[1], 2)
        self.assertEqual(X_test.shape[1], 2)

    def test_split_pandas_input(self):
        """Test splitting pandas DataFrame and Series as input."""
        X = pd.DataFrame({"a": range(10), "b": range(10, 20)})
        y = pd.Series(range(10))
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=0
        )
        self.assertEqual(len(X_train) + len(X_test), 10)
        self.assertTrue(hasattr(X_train, "iloc"))
        self.assertTrue(hasattr(y_train, "iloc"))

    def test_no_arrays_raises(self):
        """Test that passing no arrays raises ValueError."""
        with self.assertRaises(ValueError):
            train_test_split()

    def test_mismatched_array_lengths(self):
        """Test that arrays of different lengths raise ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(6)
        with self.assertRaises(ValueError):
            train_test_split(X, y)

    def test_stratify_no_shuffle_raises(self):
        """Test that stratify with shuffle=False raises ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.array([0, 1, 0, 1, 0])
        with self.assertRaises(ValueError):
            train_test_split(X, y, stratify=y, shuffle=False)

    def test_stratify_wrong_length(self):
        """Test that stratify labels of wrong length raise ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(5)
        stratify = np.arange(4)
        with self.assertRaises(ValueError):
            train_test_split(X, y, stratify=stratify)

    def test_stratify_one_class(self):
        """Test that stratify with only one unique value raises ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.zeros(5)
        with self.assertRaises(ValueError):
            train_test_split(X, y, stratify=y)

    def test_invalid_test_size_float(self):
        """Test that test_size < 0 or > 1 as float raises ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(5)
        with self.assertRaises(ValueError):
            train_test_split(X, y, test_size=-0.1)
        with self.assertRaises(ValueError):
            train_test_split(X, y, test_size=1.1)

    def test_invalid_test_size_int(self):
        """Test that test_size < 0 or > n_samples as int raises ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(5)
        with self.assertRaises(ValueError):
            train_test_split(X, y, test_size=-1)
        with self.assertRaises(ValueError):
            train_test_split(X, y, test_size=6)

    def test_sum_train_test_size_exceeds(self):
        """Test that train_size + test_size > n_samples raises ValueError."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(5)
        with self.assertRaises(ValueError):
            train_test_split(X, y, train_size=3, test_size=3)

    def test_rounding_adjustment(self):
        """Test rounding adjustment for stratified split (line 161)."""
        X = np.arange(40).reshape(20, 2)
        y = np.array([0] * 13 + [1] * 7)
        # n_samples=20, n_train=13, n_test=7, stratify=y
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.35, stratify=y, random_state=42
        )
        self.assertEqual(len(X_train), 13)
        self.assertEqual(len(X_test), 7)
        # Check that class proportions are preserved
        self.assertAlmostEqual(sum(y_train) / len(y_train), sum(y) / len(y), delta=0.1)

    def test_pandas_dataframe_and_series(self):
        """Test splitting pandas DataFrame and Series (lines 170-171)."""
        X = pd.DataFrame({"a": range(10), "b": range(10, 20)})
        y = pd.Series(range(10))
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=0
        )
        self.assertEqual(len(X_train) + len(X_test), 10)
        self.assertTrue(hasattr(X_train, "iloc"))
        self.assertTrue(hasattr(y_train, "iloc"))

    def test_list_input(self):
        """Test splitting lists (lines 173-174)."""
        X = list(range(10))
        y = list(range(10))
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=0
        )
        self.assertEqual(len(X_train) + len(X_test), 10)
        self.assertIsInstance(X_train, list)
        self.assertIsInstance(X_test, list)

    def test_stratify_wrong_length_raises(self):
        """Test that stratify labels of wrong length raise ValueError (line 58)."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(5)
        stratify = np.arange(4)
        with self.assertRaises(ValueError):
            train_test_split(X, y, stratify=stratify)

    def test_test_size_float_out_of_bounds(self):
        """Test that test_size as float <0 or >1 raises ValueError (line 97)."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(5)
        with self.assertRaises(ValueError):
            train_test_split(X, y, test_size=-0.1)
        with self.assertRaises(ValueError):
            train_test_split(X, y, test_size=1.1)

    def test_test_size_int_out_of_bounds(self):
        """Test that test_size as int <0 or >n_samples raises ValueError (line 108)."""
        X = np.arange(10).reshape(5, 2)
        y = np.arange(5)
        with self.assertRaises(ValueError):
            train_test_split(X, y, test_size=-1)
        with self.assertRaises(ValueError):
            train_test_split(X, y, test_size=6)

    def test_stratified_rounding_adjustment(self):
        """Test rounding adjustment for stratified split (line 161)."""
        X = np.arange(40).reshape(20, 2)
        y = np.array([0] * 13 + [1] * 7)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.35, stratify=y, random_state=42
        )
        self.assertEqual(len(X_train), 13)
        self.assertEqual(len(X_test), 7)
        # Check that class proportions are preserved
        self.assertAlmostEqual(sum(y_train) / len(y_train), sum(y) / len(y), delta=0.1)

    def test_pandas_dataframe_and_series_split(self):
        """Test splitting pandas DataFrame and Series (lines 170-171)."""
        X = pd.DataFrame({"a": range(10), "b": range(10, 20)})
        y = pd.Series(range(10))
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=0
        )
        self.assertEqual(len(X_train) + len(X_test), 10)
        self.assertTrue(hasattr(X_train, "iloc"))
        self.assertTrue(hasattr(y_train, "iloc"))

    def test_numpy_array_split(self):
        """Test splitting numpy arrays (lines 173-174)."""
        X = np.arange(20).reshape(10, 2)
        y = np.arange(10)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=0
        )
        self.assertEqual(X_train.shape[0] + X_test.shape[0], 10)
        self.assertIsInstance(X_train, np.ndarray)
        self.assertIsInstance(X_test, np.ndarray)


if __name__ == "__main__":
    unittest.main()
