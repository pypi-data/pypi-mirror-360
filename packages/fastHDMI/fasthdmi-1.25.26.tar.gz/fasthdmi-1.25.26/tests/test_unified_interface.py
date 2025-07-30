#!/usr/bin/env python
# coding: utf-8

"""Test unified interface and data handling."""

import numpy as np
import pandas as pd
import tempfile
import fastHDMI
from fastHDMI import screen_features, rank_features


def test_unified_interface():
    """Test the unified screening interface with different input types."""
    np.random.seed(42)
    n_samples, n_features = 1000, 20
    
    # Create test data with some informative features
    X = np.random.randn(n_samples, n_features)
    # Make first 3 features informative
    y = X[:, 0] + 0.5 * X[:, 1] + 0.3 * X[:, 2] + np.random.randn(n_samples) * 0.5
    
    print("=== Testing Unified Interface ===")
    
    # Test 1: NumPy array input
    print("\n1. NumPy array input:")
    mi_scores_array = screen_features(X, y, outcome_type='continuous', method='mi')
    print(f"MI scores shape: {mi_scores_array.shape}")
    print(f"Top 5 features: {np.argsort(mi_scores_array)[-5:][::-1]}")
    
    # Test 2: DataFrame input
    print("\n2. DataFrame input:")
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(n_features)])
    df['outcome'] = y
    
    mi_scores_df = screen_features(df, outcome='outcome', outcome_type='continuous', method='mi')
    print(f"MI scores shape: {mi_scores_df.shape}")
    print(f"Top 5 features: {np.argsort(mi_scores_df)[-5:][::-1]}")
    
    # Test 3: CSV file input
    print("\n3. CSV file input:")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        csv_path = f.name
    
    mi_scores_csv = screen_features(csv_path, outcome='outcome', outcome_type='continuous', method='mi')
    print(f"MI scores shape: {mi_scores_csv.shape}")
    print(f"Top 5 features: {np.argsort(mi_scores_csv)[-5:][::-1]}")
    
    # Test 4: Binary outcome
    print("\n4. Binary outcome:")
    y_binary = (y > np.median(y)).astype(int)
    mi_scores_binary = screen_features(X, y_binary, outcome_type='binary', method='mi')
    print(f"MI scores shape: {mi_scores_binary.shape}")
    print(f"Top 5 features: {np.argsort(mi_scores_binary)[-5:][::-1]}")
    
    # Test 5: Different methods
    print("\n5. Different screening methods:")
    methods = ['mi', 'pearson', 'binning', 'sklearn']
    
    for method in methods:
        try:
            scores = screen_features(X, y, outcome_type='continuous', method=method,
                                   bw_multiplier=1.0 if method == 'mi' else None)
            print(f"{method}: top feature = {np.argmax(scores)}, max score = {np.max(scores):.4f}")
        except Exception as e:
            print(f"{method}: Error - {str(e)}")
    
    # Test 6: Feature ranking
    print("\n6. Feature ranking:")
    rankings = rank_features(X, y, outcome_type='continuous', method='mi')
    print(f"Feature rankings shape: {rankings.shape}")
    print(f"Top 5 ranked features: {rankings[:5]}")
    
    # Test 7: Parallel processing
    print("\n7. Parallel processing:")
    mi_scores_parallel = screen_features(X, y, outcome_type='continuous', 
                                       method='mi', parallel=True, core_num=2)
    print(f"Parallel results match serial: {np.allclose(mi_scores_array, mi_scores_parallel)}")
    
    # Test 8: SNP data
    print("\n8. SNP data (0,1,2 encoding):")
    X_snp = np.random.choice([0, 1, 2], size=(n_samples, n_features), p=[0.5, 0.3, 0.2])
    y_snp = X_snp[:, 0] + 0.5 * X_snp[:, 1] + np.random.randn(n_samples) * 0.5
    
    mi_scores_snp = screen_features(X_snp, y_snp, outcome_type='continuous', 
                                  method='mi', feature_type='snp')
    print(f"SNP MI scores shape: {mi_scores_snp.shape}")
    print(f"Top 5 SNP features: {np.argsort(mi_scores_snp)[-5:][::-1]}")
    
    print("\n✓ All unified interface tests completed successfully!")


if __name__ == "__main__":
    test_unified_interface()