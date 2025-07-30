#!/usr/bin/env python3
"""Integration tests for fastHDMI package."""

import unittest
import numpy as np
import pandas as pd
import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import fastHDMI


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple fastHDMI functions."""
    
    def setUp(self):
        """Set up test data for integration tests."""
        np.random.seed(42)
        self.n_samples = 200
        self.n_features = 50
        
        # Create high-dimensional data with sparse true model
        self.X = np.random.randn(self.n_samples, self.n_features)
        
        # True model: only first 5 features are relevant
        self.beta_true = np.zeros(self.n_features)
        self.beta_true[:5] = [3.0, -2.5, 2.0, -1.5, 1.0]
        
        # Generate response
        self.y = self.X @ self.beta_true + np.random.randn(self.n_samples) * 0.5
        
        # Binary response
        logits = self.X @ self.beta_true
        probs = 1 / (1 + np.exp(-logits))
        self.y_binary = (np.random.rand(self.n_samples) < probs).astype(int)
        
    def test_screening_pipeline(self):
        """Test screening pipeline."""
        # Step 1: Screen features using MI
        mi_scores = fastHDMI.continuous_screening_array(self.X, self.y)
        
        # Select top 10 features
        n_selected = 10
        top_features = np.argsort(mi_scores)[-n_selected:]
        X_screened = self.X[:, top_features]
        
        # Verify that true features are selected
        true_features_selected = sum(i in top_features for i in range(5))
        self.assertGreaterEqual(true_features_selected, 4,
                               "At least 4 of 5 true features should be selected")
        
    def test_parallel_screening_consistency(self):
        """Test that parallel screening gives consistent results."""
        # Array screening
        mi_single = fastHDMI.continuous_screening_array(self.X, self.y)
        mi_parallel = fastHDMI.continuous_screening_array_parallel(
            self.X, self.y, core_num=2
        )
        
        np.testing.assert_array_almost_equal(
            mi_single, mi_parallel, decimal=4,
            err_msg="Single and parallel array screening should match"
        )
        
        # Create temporary CSV for testing
        df = pd.DataFrame(self.X, columns=[f'feature_{i}' for i in range(self.n_features)])
        df['outcome'] = self.y
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            temp_csv = f.name
            
        try:
            # CSV screening
            mi_csv_single = fastHDMI.continuous_screening_csv(temp_csv)
            mi_csv_parallel = fastHDMI.continuous_screening_csv_parallel(
                temp_csv, core_num=2
            )
            
            np.testing.assert_array_almost_equal(
                mi_csv_single, mi_csv_parallel, decimal=4,
                err_msg="Single and parallel CSV screening should match"
            )
        finally:
            os.unlink(temp_csv)
            
    def test_different_screening_methods(self):
        """Test that different screening methods work correctly."""
        # KDE-based MI
        mi_kde = fastHDMI.continuous_screening_array(self.X, self.y)
        
        # Create DataFrame for other methods
        df = pd.DataFrame(self.X, columns=[f'feature_{i}' for i in range(self.n_features)])
        df['outcome'] = self.y
        
        # Test DataFrame screening - outcome should be first column
        df_reordered = df[['outcome'] + [f'feature_{i}' for i in range(self.n_features)]]
        mi_df = fastHDMI.continuous_screening_dataframe(df_reordered)
        
        # Arrays should give same results as DataFrames
        # DataFrame screening calculates MI between outcome (first column) and all other features
        # Array screening calculates MI between y and all features in X
        # Both should give the same results
        np.testing.assert_array_almost_equal(
            mi_kde, mi_df, decimal=4,
            err_msg="Array and DataFrame screening should match"
        )
        
    def test_binary_outcome_screening(self):
        """Test screening with binary outcome."""
        # Binary screening
        mi_scores = fastHDMI.binary_screening_array(self.X, self.y_binary)
        
        # Select top features
        n_selected = 15
        top_features = np.argsort(mi_scores)[-n_selected:]
        
        # Verify that true features are selected
        true_features_selected = sum(i in top_features for i in range(5))
        self.assertGreaterEqual(true_features_selected, 3,
                               "At least 3 of 5 true features should be selected")
        
    def test_snp_data_screening(self):
        """Test screening for SNP data."""
        # Create SNP data
        n_snps = 30
        X_snp = np.random.choice([0, 1, 2], 
                                size=(self.n_samples, n_snps),
                                p=[0.25, 0.5, 0.25])
        
        # Create phenotype with first 3 SNPs having effects
        beta_snp = np.zeros(n_snps)
        beta_snp[:3] = [0.5, -0.3, 0.4]
        y_snp = X_snp @ beta_snp + np.random.randn(self.n_samples) * 0.5
        
        # Screen SNPs
        mi_scores = fastHDMI.continuous_screening_array(X_snp, y_snp)
        
        # Check that true SNPs have high MI scores
        top_10_indices = np.argsort(mi_scores)[-10:]
        true_snps_in_top = sum(i in top_10_indices for i in range(3))
        self.assertGreaterEqual(true_snps_in_top, 2,
                               "At least 2 of 3 true SNPs should be in top 10")
                
    def test_clumping_workflow(self):
        """Test feature clumping workflow."""
        # Create correlated features
        n_groups = 10
        n_per_group = 5
        n_features_total = n_groups * n_per_group
        
        # Generate correlated feature groups
        X_corr = np.zeros((self.n_samples, n_features_total))
        for g in range(n_groups):
            # Base feature for group
            base = np.random.randn(self.n_samples)
            for i in range(n_per_group):
                idx = g * n_per_group + i
                # Add correlation within groups
                X_corr[:, idx] = base + np.random.randn(self.n_samples) * 0.3
                
        # Create outcome depending on one feature per group
        y_corr = sum(X_corr[:, g * n_per_group] for g in range(n_groups))
        y_corr += np.random.randn(self.n_samples) * 0.5
        
        # Create DataFrame
        df_corr = pd.DataFrame(X_corr, columns=[f'feature_{i}' for i in range(n_features_total)])
        df_corr['outcome'] = y_corr
        
        # Perform clumping - outcome should be first column
        df_clump = df_corr[['outcome'] + list(df_corr.columns[:-1])]
        mi_clumped = fastHDMI.clump_continuous_dataframe_parallel(
            df_clump, 
            threshold=0.5,  # MI threshold for clumping
            num_vars_exam=20
        )
        var_names_clumped = list(range(len(mi_clumped)))
        
        # Should select fewer features than total
        self.assertLess(len(var_names_clumped), n_features_total,
                       "Clumping should reduce number of features")
        
        # Ideally, should select approximately one per group
        self.assertLessEqual(len(var_names_clumped), n_groups * 2,
                            "Should select roughly one feature per correlated group")
        
    def test_performance_metrics(self):
        """Test that key operations complete in reasonable time."""
        import time
        
        # Test screening performance
        start_time = time.time()
        mi_scores = fastHDMI.continuous_screening_array(self.X, self.y)
        screening_time = time.time() - start_time
        
        self.assertLess(screening_time, 5.0,
                       f"Screening {self.n_features} features should take < 5 seconds")
        
        # Test parallel screening performance
        start_time = time.time()
        mi_scores_parallel = fastHDMI.continuous_screening_array_parallel(
            self.X, self.y, core_num=2
        )
        parallel_screening_time = time.time() - start_time
        
        # Parallel should not be much slower (overhead considered)
        self.assertLess(parallel_screening_time, screening_time * 2,
                       "Parallel screening should not be much slower than single-threaded")
        
    def test_reproducibility(self):
        """Test that results are reproducible with same random seed."""
        # Run screening twice with same data
        mi_scores_1 = fastHDMI.continuous_screening_array(self.X, self.y)
        mi_scores_2 = fastHDMI.continuous_screening_array(self.X, self.y)
        
        np.testing.assert_array_almost_equal(
            mi_scores_1, mi_scores_2,
            err_msg="Results should be deterministic"
        )
        


if __name__ == '__main__':
    unittest.main()