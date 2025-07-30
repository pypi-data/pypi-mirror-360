#!/usr/bin/env python
# coding: utf-8

"""Test Cython performance improvements."""

import time
import numpy as np
import fastHDMI
from fastHDMI.mi_estimation.mi_estimation import (
    _hist_obj, _num_of_bins, _joint_to_mi, _nan_inf_to_0,
    hist_obj_cython, num_of_bins_cython, joint_to_mi_cython,
    nan_inf_to_0_cython, Pearson_to_MI_Gaussian_cython,
    MI_to_Linfoot_cython, CYTHON_AVAILABLE
)


def benchmark_function(func, *args, n_runs=100):
    """Benchmark a function."""
    times = []
    for _ in range(n_runs):
        start = time.time()
        result = func(*args)
        times.append(time.time() - start)
    return np.mean(times), np.std(times), result


def main():
    print(f"Cython available: {CYTHON_AVAILABLE}")
    
    if not CYTHON_AVAILABLE:
        print("Cython not available, skipping performance tests")
        return
    
    # Test data
    np.random.seed(42)
    x = np.random.randn(1000)
    joint = np.random.rand(50, 50)
    joint /= joint.sum()
    joint = np.ascontiguousarray(joint)
    
    print("\n=== Performance Comparison ===")
    
    # Test hist_obj
    print("\n1. hist_obj function:")
    time_py, std_py, res_py = benchmark_function(_hist_obj, x, 10)
    time_cy, std_cy, res_cy = benchmark_function(hist_obj_cython, x, 10)
    print(f"Python: {time_py*1000:.4f} ± {std_py*1000:.4f} ms")
    print(f"Cython: {time_cy*1000:.4f} ± {std_cy*1000:.4f} ms")
    print(f"Speedup: {time_py/time_cy:.2f}x")
    print(f"Results match: {np.allclose(res_py, res_cy)}")
    
    # Test num_of_bins
    print("\n2. num_of_bins function:")
    time_py, std_py, res_py = benchmark_function(_num_of_bins, x, n_runs=10)
    time_cy, std_cy, res_cy = benchmark_function(num_of_bins_cython, x, n_runs=10)
    print(f"Python: {time_py*1000:.4f} ± {std_py*1000:.4f} ms")
    print(f"Cython: {time_cy*1000:.4f} ± {std_cy*1000:.4f} ms")
    print(f"Speedup: {time_py/time_cy:.2f}x")
    print(f"Results match: {res_py == res_cy}")
    
    # Test joint_to_mi
    print("\n3. joint_to_mi function:")
    time_py, std_py, res_py = benchmark_function(_joint_to_mi, joint.copy(), 1.0, 1.0)
    time_cy, std_cy, res_cy = benchmark_function(joint_to_mi_cython, joint.copy(), 1.0, 1.0)
    print(f"Python: {time_py*1000:.4f} ± {std_py*1000:.4f} ms")
    print(f"Cython: {time_cy*1000:.4f} ± {std_cy*1000:.4f} ms")
    print(f"Speedup: {time_py/time_cy:.2f}x")
    print(f"Results match: {np.allclose(res_py, res_cy)}")
    
    # Test nan_inf_to_0
    print("\n4. nan_inf_to_0 function:")
    x_with_nan = x.copy()
    x_with_nan[::10] = np.nan
    x_with_nan[::20] = np.inf
    time_py, std_py, res_py = benchmark_function(_nan_inf_to_0, x_with_nan)
    time_cy, std_cy, res_cy = benchmark_function(nan_inf_to_0_cython, x_with_nan)
    print(f"Python: {time_py*1000:.4f} ± {std_py*1000:.4f} ms")
    print(f"Cython: {time_cy*1000:.4f} ± {std_cy*1000:.4f} ms")
    print(f"Speedup: {time_py/time_cy:.2f}x")
    print(f"Results match: {np.allclose(res_py, res_cy, equal_nan=True)}")
    
    # Test Pearson_to_MI_Gaussian
    print("\n5. Pearson_to_MI_Gaussian function:")
    correlations = np.linspace(-0.99, 0.99, 100)
    
    def pearson_py(corr):
        if corr == -1 or corr == 1:
            return np.inf
        return -0.5 * np.log1p(-corr**2)
    
    time_py = 0
    time_cy = 0
    for corr in correlations:
        t1 = time.time()
        res_py = pearson_py(corr)
        time_py += time.time() - t1
        
        t1 = time.time()
        res_cy = Pearson_to_MI_Gaussian_cython(corr)
        time_cy += time.time() - t1
    
    print(f"Python: {time_py*1000:.4f} ms (total for 100 correlations)")
    print(f"Cython: {time_cy*1000:.4f} ms (total for 100 correlations)")
    print(f"Speedup: {time_py/time_cy:.2f}x")
    
    # Test MI estimation with larger data
    print("\n6. Full MI estimation performance:")
    X = np.random.randn(5000, 2)
    
    start = time.time()
    mi = fastHDMI.MI_continuous_continuous(X[:, 0], X[:, 1], bw_multiplier=1.0)
    total_time = time.time() - start
    
    print(f"MI estimation time: {total_time*1000:.2f} ms")
    print(f"MI value: {mi:.6f}")
    
    # Check hardware acceleration
    print("\n=== Hardware Acceleration ===")
    print(f"AVX2 support: {fastHDMI.supports_avx2()}")
    
    try:
        from fastHDMI.utils.hardware_detection import get_cpu_features
        features = get_cpu_features()
        print("Available SIMD features:")
        for feature, available in features.items():
            if available:
                print(f"  - {feature}")
    except ImportError:
        print("Hardware detection module not available")


if __name__ == "__main__":
    main()