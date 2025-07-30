#!/usr/bin/env python3
"""Tests for MI estimation functions."""

import unittest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import fastHDMI


class TestMIEstimation(unittest.TestCase):
    """Test mutual information estimation functions."""
    
    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.n_samples = 1000
        
    def test_mi_continuous_continuous(self):
        """Test MI between two continuous variables."""
        # Test correlated variables
        x = np.random.randn(self.n_samples)
        y = 2 * x + np.random.randn(self.n_samples) * 0.5
        
        mi = fastHDMI.MI_continuous_continuous(x, y, bw_multiplier=1.0)
        self.assertGreater(mi, 0, "MI should be positive for correlated variables")
        self.assertTrue(np.isfinite(mi), "MI should be finite")
        
        # Test independent variables
        x_ind = np.random.randn(self.n_samples)
        y_ind = np.random.randn(self.n_samples)
        
        mi_ind = fastHDMI.MI_continuous_continuous(x_ind, y_ind, bw_multiplier=1.0)
        self.assertLess(mi_ind, mi, "MI should be lower for independent variables")
        self.assertGreaterEqual(mi_ind, 0, "MI should be non-negative")
        
    def test_mi_binary_continuous(self):
        """Test MI between binary and continuous variables."""
        # Binary variable
        x_binary = np.random.choice([0, 1], size=self.n_samples)
        # Continuous variable dependent on binary
        y = x_binary * 2 + np.random.randn(self.n_samples)
        
        mi = fastHDMI.MI_binary_continuous(x_binary, y, bw_multiplier=1.0)
        self.assertGreaterEqual(mi, 0, "MI should be non-negative")
        self.assertTrue(np.isfinite(mi), "MI should be finite")
        
    def test_mi_continuous_012(self):
        """Test MI between continuous and SNP-like (0,1,2) variables."""
        # SNP-like variable
        snp = np.random.choice([0, 1, 2], size=self.n_samples, p=[0.25, 0.5, 0.25])
        # Continuous variable dependent on SNP
        y = snp * 1.5 + np.random.randn(self.n_samples)
        
        mi = fastHDMI.MI_continuous_012(y, snp, bw_multiplier=1.0)
        self.assertGreaterEqual(mi, 0, "MI should be non-negative")
        self.assertTrue(np.isfinite(mi), "MI should be finite")
        
    def test_mi_binary_012(self):
        """Test MI between binary and SNP variables."""
        # Binary variable
        binary = np.random.choice([0, 1], size=self.n_samples)
        # SNP variable correlated with binary
        snp = np.random.choice([0, 1, 2], size=self.n_samples, 
                              p=[0.3 - 0.1*binary.mean(), 0.4, 0.3 + 0.1*binary.mean()])
        
        mi = fastHDMI.MI_binary_012(binary, snp)
        self.assertGreaterEqual(mi, 0, "MI should be non-negative")
        self.assertTrue(np.isfinite(mi), "MI should be finite")
        
    def test_mi_012_012(self):
        """Test MI between two SNP variables."""
        # Two correlated SNP variables
        snp1 = np.random.choice([0, 1, 2], size=self.n_samples, p=[0.25, 0.5, 0.25])
        # Second SNP correlated with first
        # Create probability matrix based on snp1 values
        p2 = np.zeros((self.n_samples, 3))
        p2[snp1 == 0] = [0.4, 0.4, 0.2]
        p2[snp1 == 1] = [0.2, 0.6, 0.2]
        p2[snp1 == 2] = [0.1, 0.4, 0.5]
        snp2 = np.array([np.random.choice([0, 1, 2], p=p2[i]) for i in range(self.n_samples)])
        
        mi = fastHDMI.MI_012_012(snp1, snp2)
        self.assertGreaterEqual(mi, 0, "MI should be non-negative")
        self.assertTrue(np.isfinite(mi), "MI should be finite")
        
    def test_pearson_to_mi_gaussian(self):
        """Test Pearson correlation to MI conversion."""
        test_correlations = [0.0, 0.3, 0.5, 0.7, 0.9]
        
        for r in test_correlations:
            mi = fastHDMI.Pearson_to_MI_Gaussian(r)
            self.assertGreaterEqual(mi, 0, f"MI should be non-negative for r={r}")
            
            # Test that higher correlation gives higher MI
            if r > 0:
                mi_smaller = fastHDMI.Pearson_to_MI_Gaussian(r * 0.9)
                self.assertGreater(mi, mi_smaller, 
                                 f"Higher correlation should give higher MI")
        
        # Test edge cases
        mi_perfect = fastHDMI.Pearson_to_MI_Gaussian(1.0)
        self.assertEqual(mi_perfect, np.inf, "Perfect correlation should give infinite MI")
        
        mi_negative_perfect = fastHDMI.Pearson_to_MI_Gaussian(-1.0)
        self.assertEqual(mi_negative_perfect, np.inf, "Perfect negative correlation should give infinite MI")
        
    def test_mi_to_linfoot(self):
        """Test MI to Linfoot conversion."""
        # Test various MI values
        mi_values = [0.0, 0.1, 0.5, 1.0, 2.0]
        
        for mi in mi_values:
            linfoot = fastHDMI.MI_to_Linfoot(mi)
            self.assertGreaterEqual(linfoot, 0, f"Linfoot should be non-negative for MI={mi}")
            self.assertLessEqual(linfoot, 1, f"Linfoot should be <= 1 for MI={mi}")
            
            # Test that higher MI gives higher Linfoot
            if mi > 0:
                linfoot_smaller = fastHDMI.MI_to_Linfoot(mi * 0.9)
                self.assertGreater(linfoot, linfoot_smaller,
                                 f"Higher MI should give higher Linfoot correlation")
        
    def test_mi_with_nan_values(self):
        """Test MI estimation with NaN values."""
        x = np.random.randn(self.n_samples)
        y = 2 * x + np.random.randn(self.n_samples) * 0.5
        
        # Add some NaN values
        x[::10] = np.nan
        y[5::10] = np.nan
        
        # MI functions should handle NaN values gracefully
        mi = fastHDMI.MI_continuous_continuous(x, y, bw_multiplier=1.0)
        self.assertTrue(np.isfinite(mi), "MI should be finite even with NaN values")
        self.assertGreaterEqual(mi, 0, "MI should be non-negative")
        
    def test_different_kernels_and_bandwidths(self):
        """Test MI estimation with different kernels and bandwidth methods."""
        x = np.random.randn(self.n_samples)
        y = 2 * x + np.random.randn(self.n_samples) * 0.5
        
        kernels = ['gaussian', 'epa', 'tri', 'biweight', 'triweight']
        bw_methods = ['silverman', 'scott', 'ISJ']
        
        mi_values = []
        for kernel in kernels:
            for bw in bw_methods:
                try:
                    mi = fastHDMI.MI_continuous_continuous(x, y, bw_multiplier=1.0, kernel=kernel, bw=bw)
                    self.assertGreaterEqual(mi, 0, f"MI should be non-negative for kernel={kernel}, bw={bw}")
                    self.assertTrue(np.isfinite(mi), f"MI should be finite for kernel={kernel}, bw={bw}")
                    mi_values.append(mi)
                except:
                    # Some combinations might not be supported
                    pass
        
        # All MI estimates should be reasonably similar for the same data
        if len(mi_values) > 1:
            mi_std = np.std(mi_values)
            mi_mean = np.mean(mi_values)
            self.assertLess(mi_std / mi_mean, 0.5, "MI estimates should be reasonably consistent across methods")


if __name__ == '__main__':
    unittest.main()