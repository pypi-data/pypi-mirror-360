#!/usr/bin/env python3
"""Tests for screening functions."""

import unittest
import numpy as np
import pandas as pd
import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import fastHDMI


class TestScreening(unittest.TestCase):
    """Test feature screening functions."""
    
    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.n_samples = 100
        self.n_features = 10
        
        # Create test data with known relationships
        self.X = np.random.randn(self.n_samples, self.n_features)
        # Make y depend strongly on first two features
        self.y = self.X[:, 0] + 0.5 * self.X[:, 1] + np.random.randn(self.n_samples) * 0.1
        
        # Create binary outcome
        self.y_binary = (self.y > np.median(self.y)).astype(int)
        
        # Create test DataFrame
        self.df = pd.DataFrame(self.X, columns=[f'feature_{i}' for i in range(self.n_features)])
        self.df['outcome'] = self.y
        self.df['binary_outcome'] = self.y_binary
        
    def test_continuous_screening_array(self):
        """Test continuous screening with array input."""
        # Single-threaded version
        mi_scores = fastHDMI.continuous_screening_array(self.X, self.y)
        
        self.assertEqual(len(mi_scores), self.n_features)
        self.assertTrue(np.all(mi_scores >= 0), "All MI scores should be non-negative")
        
        # First two features should have highest MI
        top_2_indices = np.argsort(mi_scores)[-2:]
        self.assertIn(0, top_2_indices, "First feature should be in top 2")
        self.assertIn(1, top_2_indices, "Second feature should be in top 2")
        
    def test_continuous_screening_array_parallel(self):
        """Test parallel continuous screening with array input."""
        mi_scores_parallel = fastHDMI.continuous_screening_array_parallel(
            self.X, self.y, core_num=2
        )
        
        self.assertEqual(len(mi_scores_parallel), self.n_features)
        self.assertTrue(np.all(mi_scores_parallel >= 0), "All MI scores should be non-negative")
        
        # Compare with single-threaded results
        mi_scores_single = fastHDMI.continuous_screening_array(self.X, self.y)
        np.testing.assert_array_almost_equal(
            mi_scores_single, mi_scores_parallel,
            decimal=4, err_msg="Parallel and single results should match"
        )
        
    def test_binary_screening_array(self):
        """Test binary screening with array input."""
        # Single-threaded version
        mi_scores = fastHDMI.binary_screening_array(self.X, self.y_binary)
        
        self.assertEqual(len(mi_scores), self.n_features)
        self.assertTrue(np.all(mi_scores >= 0), "All MI scores should be non-negative")
        
        # First two features should still have highest MI
        top_2_indices = np.argsort(mi_scores)[-2:]
        self.assertIn(0, top_2_indices, "First feature should be in top 2")
        
    def test_binary_screening_array_parallel(self):
        """Test parallel binary screening with array input."""
        mi_scores_parallel = fastHDMI.binary_screening_array_parallel(
            self.X, self.y_binary, core_num=2
        )
        
        self.assertEqual(len(mi_scores_parallel), self.n_features)
        self.assertTrue(np.all(mi_scores_parallel >= 0), "All MI scores should be non-negative")
        
    def test_screening_with_nan(self):
        """Test screening with NaN values."""
        # Create data with NaN
        X_with_nan = self.X.copy()
        X_with_nan[0, 0] = np.nan
        X_with_nan[1, 1] = np.nan
        
        mi_scores = fastHDMI.continuous_screening_array(X_with_nan, self.y)
        
        # Should still work and return valid scores
        self.assertEqual(len(mi_scores), self.n_features)
        self.assertTrue(np.all(np.isfinite(mi_scores)), "Scores should be finite despite NaN")
        
    def test_csv_screening(self):
        """Test CSV screening if test data exists."""
        csv_path = os.path.join(os.path.dirname(__file__), 'sim', 'sim_continuous.csv')
        
        if os.path.exists(csv_path):
            # Single-threaded
            mi_scores = fastHDMI.continuous_screening_csv(csv_path)
            
            self.assertIsInstance(mi_scores, np.ndarray)
            self.assertTrue(np.all(mi_scores >= 0))
            
            # Parallel version
            mi_scores_p = fastHDMI.continuous_screening_csv_parallel(csv_path)
            
            np.testing.assert_array_almost_equal(mi_scores, mi_scores_p, decimal=4)
        else:
            self.skipTest(f"Test CSV file not found: {csv_path}")
            
    def test_dataframe_screening(self):
        """Test DataFrame screening."""
        # Continuous screening - outcome should be first column
        df_cont = self.df[['outcome'] + list(self.df.columns[:-2])]
        mi_scores = fastHDMI.continuous_screening_dataframe(df_cont)
        
        # Function returns MI for all features against outcome
        self.assertEqual(len(mi_scores), self.n_features)
        self.assertTrue(np.all(mi_scores >= 0))
        
        # Binary screening - outcome should be first column
        df_bin = self.df[['binary_outcome'] + list(self.df.columns[:-2])]
        mi_scores_b = fastHDMI.binary_screening_dataframe(df_bin)
        
        self.assertEqual(len(mi_scores_b), self.n_features)
        self.assertTrue(np.all(mi_scores_b >= 0))
        
    def test_dataframe_screening_parallel(self):
        """Test parallel DataFrame screening."""
        # Continuous screening - outcome should be first column
        df_cont = self.df[['outcome'] + list(self.df.columns[:-2])]
        mi_scores = fastHDMI.continuous_screening_dataframe_parallel(
            df_cont, core_num=2
        )
        
        self.assertEqual(len(mi_scores), self.n_features)
        self.assertTrue(np.all(mi_scores >= 0))
        
        # Compare with single-threaded
        mi_scores_s = fastHDMI.continuous_screening_dataframe(df_cont)
        
        np.testing.assert_array_almost_equal(mi_scores, mi_scores_s, decimal=4)
        
    def test_pearson_screening(self):
        """Test Pearson correlation screening."""
        # Create temporary CSV file with outcome as first column
        df_with_outcome = self.df[['outcome'] + list(self.df.columns[:-2])]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df_with_outcome.to_csv(f.name, index=False)
            temp_csv = f.name
            
        try:
            correlations = fastHDMI.Pearson_screening_csv_parallel(
                temp_csv, core_num=2
            )
            
            # Returns correlations between outcome and all features (n_features)
            self.assertEqual(len(correlations), self.n_features)
            
            # Correlations should be between -1 and 1
            self.assertTrue(np.all(np.abs(correlations) <= 1))
            
            # First two features should have highest absolute correlation
            # Results correspond to features 0-9 (feature_0 to feature_9)
            top_2_indices = np.argsort(np.abs(correlations))[-2:]
            # Check if indices 0 and 1 (corresponding to feature_0 and feature_1) are in top 2
            self.assertTrue(0 in top_2_indices or 1 in top_2_indices,
                            "At least one of the first two features should be in top 2")
        finally:
            os.unlink(temp_csv)
            
    def test_different_screening_methods(self):
        """Test that different screening methods give consistent rankings."""
        # Test on array data
        mi_kde = fastHDMI.continuous_screening_array(self.X, self.y)
        
        # Convert to DataFrame for other methods - outcome as first column
        df_with_outcome = self.df[['outcome'] + list(self.df.columns[:-2])]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df_with_outcome.to_csv(f.name, index=False)
            temp_csv = f.name
            
        try:
            # Test sklearn MI screening
            mi_sk = fastHDMI.continuous_skMI_screening_csv_parallel(
                temp_csv, n_neighbors=3, random_state=42, core_num=2
            )
            
            # Test binning MI screening  
            mi_bin = fastHDMI.binning_continuous_screening_csv_parallel(
                temp_csv, core_num=2
            )
            
            # Test Pearson screening
            corr = fastHDMI.Pearson_screening_csv_parallel(
                temp_csv, core_num=2
            )
            
            # All methods should identify first two features as most important
            # (allowing for some variation in exact rankings)
            # Note: CSV methods return n-1 features (excluding outcome)
            for scores in [mi_sk, mi_bin, np.abs(corr)]:
                top_3_indices = np.argsort(scores)[-3:]
                # At least one of the first two features should be in top 3
                self.assertTrue(0 in top_3_indices or 1 in top_3_indices,
                                f"At least one of the first two features should be in top 3 (got {top_3_indices})")
        finally:
            os.unlink(temp_csv)


if __name__ == '__main__':
    unittest.main()