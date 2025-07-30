#!/usr/bin/env python
# coding: utf-8

"""MI estimation functions."""

import warnings as _warnings
import numpy as _np
from numba import njit as _njit
from sklearn.preprocessing import RobustScaler as _scaler
from KDEpy import FFTKDE as _FFTKDE
from KDEpy.bw_selection import silvermans_rule as _silvermans_rule
from KDEpy.bw_selection import improved_sheather_jones as _improved_sheather_jones
from KDEpy.bw_selection import scotts_rule as _scotts_rule
import os

# Import utils
from ..utils import supports_avx2


try:
    from ..cython_fun import (
        joint_to_mi_cython, hist_obj_cython, num_of_bins_cython,
        nan_inf_to_0_cython, Pearson_to_MI_Gaussian_cython, MI_to_Linfoot_cython
    )
    CYTHON_AVAILABLE = True
except ImportError:
    # Fallback if Cython unavailable
    CYTHON_AVAILABLE = False
    hist_obj_cython = None
    num_of_bins_cython = None
    joint_to_mi_cython = None
    nan_inf_to_0_cython = None
    Pearson_to_MI_Gaussian_cython = None
    MI_to_Linfoot_cython = None

_warnings.filterwarnings('ignore')


# Helper functions

def _hist_obj(x, D):
    """Calculate histogram objective function (Birge & Rozenholc method)."""
    N_j, _ = _np.histogram(
        x, bins=D)  # to get the number of data points in each bin
    return _np.sum(
        N_j * _np.log(N_j)) + len(x) * _np.log(D) - (D - 1 + _np.log(D)**2.5)


def _num_of_bins(x):
    """Calculate optimal bin count (Birge & Rozenholc method)."""
    D_list = _np.arange(
        2, 100)  # search for the optimal number of bins from 2 to 100
    if CYTHON_AVAILABLE:
        D_obj_list = _np.array([hist_obj_cython(x, D) for D in D_list])
    else:
        D_obj_list = _np.array([_hist_obj(x, D) for D in D_list])
    return D_list[_np.nanargmax(D_obj_list)]


def _binning_MI(a, b):
    """MI between continuous variables using binning."""
    joint, _, _ = _np.histogram2d(a,
                                  b,
                                  bins=(_num_of_bins(a), _num_of_bins(b)))
    joint /= _np.sum(joint)
    # Convert joint to a contiguous array for performance
    joint = _np.ascontiguousarray(joint)
    if CYTHON_AVAILABLE:
        return joint_to_mi_cython(joint, forward_euler_a=1.0)
    else:
        return _joint_to_mi(joint, forward_euler_a=1.0)


def _binning_MI_discrete(a, b):
    """MI between discrete and continuous variables using binning."""
    joint, _, _ = _np.histogram2d(a,
                                  b,
                                  bins=(len(_np.unique(a)), _num_of_bins(b)))
    joint /= _np.sum(joint)
    # Convert joint to a contiguous array for performance
    joint = _np.ascontiguousarray(joint)
    if CYTHON_AVAILABLE:
        return joint_to_mi_cython(joint, forward_euler_a=1.0)
    else:
        return _joint_to_mi(joint, forward_euler_a=1.0)


def _nan_inf_to_0(x):
    """Replace NaN/inf with zero."""
    x = x.copy()
    x[_np.isnan(x) | _np.isinf(x)] = 0.0
    return x


def _compute_log_marginals(joint, forward_euler_a, forward_euler_b):
    """Compute log marginals from joint."""
    log_marginal_x = _np.log(_np.sum(joint, axis=1)) + _np.log(forward_euler_b)
    log_marginal_y = _np.log(_np.sum(joint, axis=0)) + _np.log(forward_euler_a)
    return _nan_inf_to_0(log_marginal_x), _nan_inf_to_0(log_marginal_y)


def _joint_to_mi(joint, forward_euler_a=1., forward_euler_b=1.):
    """MI from joint distribution."""
    joint /= _np.sum(joint) * forward_euler_a * forward_euler_b
    log_marginal_a, log_marginal_b = _compute_log_marginals(
        joint, forward_euler_a, forward_euler_b)
    log_joint = _nan_inf_to_0(_np.log(joint))
    mi_temp = _np.sum(
        joint *
        (log_joint - log_marginal_a.reshape(-1, 1) -
         log_marginal_b.reshape(1, -1))) * forward_euler_a * forward_euler_b
    return max(mi_temp, 0.0)


# Bandwidth selection

def _select_bandwidth(input_var, bw_multiplier, bw="silverman"):
    """Select bandwidth for univariate data."""
    bandwidth_functions = {
        "silverman": _silvermans_rule,
        "scott": _scotts_rule,
        "ISJ": _improved_sheather_jones
    }

    if isinstance(bw, str):
        _bw = bandwidth_functions[bw](input_var.reshape(-1, 1))
    elif isinstance(bw, float):
        _bw = bw
    else:
        raise ValueError("Invalid bandwidth selection method.")

    return _bw * bw_multiplier


def _univariate_bw(input_var, bw_multiplier, bw="silverman"):
    """Get univariate bandwidth."""
    return _select_bandwidth(input_var, bw_multiplier, bw)


def _bivariate_bw(_data, bw_multiplier, bw="silverman"):
    """Get bivariate bandwidth."""
    if isinstance(bw, str):
        bw1 = _select_bandwidth(_data[:, [0]], bw_multiplier, bw)
        bw2 = _select_bandwidth(_data[:, [1]], bw_multiplier, bw)
    elif isinstance(bw, (_np.ndarray, list)) and len(bw) == 2:
        bw1, bw2 = bw[0], bw[1]
    else:
        raise ValueError("Invalid bandwidth selection for bivariate data.")

    return bw1 * bw_multiplier, bw2 * bw_multiplier


# Main MI functions

def MI_continuous_012(a,
                      b,
                      bw_multiplier,
                      N=500,
                      kernel="epa",
                      bw="silverman",
                      **kwarg):
    """MI between continuous and SNP (0,1,2) variables."""
    # Filter out NaN values
    valid_mask = ~(_np.isnan(a) | _np.isnan(b))
    a = a[valid_mask]
    b = b[valid_mask]
    
    # Calculate the probabilities for each SNP value
    p0 = _np.count_nonzero(b == 0) / len(b)
    p1 = _np.count_nonzero(b == 1) / len(b)
    p2 = 1. - p0 - p1

    # Standardize 'a'
    _a = _scaler().fit_transform(a.reshape(-1, 1)).flatten()

    # Get the boundary width for the joint density grid
    _bw = _univariate_bw(_a, bw_multiplier, bw)
    # Create evaluation grid that safely contains all data with margin
    a_min, a_max = _a.min(), _a.max()
    a_range = a_max - a_min
    margin = max(0.1, a_range * 0.1)  # 10% margin or 0.1, whichever is larger
    a_temp = _np.linspace(a_min - margin, a_max + margin, N)

    # Initialize joint distribution array
    joint = _np.zeros((N, 3))

    # Calculate conditional densities for each SNP value
    for i, (p,
            condition) in enumerate(zip([p0, p1, p2],
                                        [b == 0, b == 1, b == 2])):
        if _np.count_nonzero(condition) > 2:
            _bw = _univariate_bw(_a[condition], bw_multiplier, bw)
            # Ensure bandwidth is not too small relative to evaluation grid
            min_bw = (a_temp[1] - a_temp[0]) * 2  # At least 2x the grid resolution
            _bw = max(_bw, min_bw)
            
            # For binary/discrete outcomes, increase bandwidth if conditional distributions are well-separated
            if len(_np.unique(b)) == 2:  # Binary outcome
                # Calculate separation between conditional distributions
                other_conditions = [b == j for j in [0, 1, 2] if j != i and _np.count_nonzero(b == j) > 2]
                if other_conditions:
                    other_condition = other_conditions[0]  # Take the first valid other condition
                    if _np.count_nonzero(other_condition) > 2:
                        _a_other = _a[other_condition]
                        _a_current = _a[condition]
                        
                        # Calculate separation measure
                        mean_diff = abs(_a_current.mean() - _a_other.mean())
                        pooled_std = _np.sqrt((_a_current.std()**2 + _a_other.std()**2) / 2)
                        
                        if pooled_std > 0:
                            separation = mean_diff / pooled_std
                            # Increase bandwidth for well-separated distributions
                            if separation > 0.5:  # If moderately separated
                                _bw *= max(1.0, separation / 2.0)
            
            kde = _FFTKDE(kernel=kernel, bw=_bw).fit(data=_a[condition])
            joint[:, i] = kde.evaluate(a_temp)[0] * p
        # No else block needed; joint[:, i] is already initialized with zeros

    # Calculate the forward Euler step
    forward_euler_step = a_temp[1] - a_temp[0]

    # Ensure all values in joint are non-negative
    joint = _np.clip(joint, 0, None)

    # Convert joint to a contiguous array for performance
    joint = _np.ascontiguousarray(joint)

    if CYTHON_AVAILABLE:
        return joint_to_mi_cython(joint=joint, forward_euler_a=forward_euler_step)
    else:
        return _joint_to_mi(joint=joint, forward_euler_a=forward_euler_step)


def MI_binary_012(a, b):
    """MI between binary and SNP variables."""
    return MI_012_012(a, b)


def MI_012_012(a, b):
    """MI between two SNP variables."""
    joint = _np.array([[(_np.logical_and(a == i, b == j)).sum() / len(a)
                        for j in range(3)] for i in range(3)])
    if CYTHON_AVAILABLE:
        return joint_to_mi_cython(joint=_np.ascontiguousarray(joint), forward_euler_a=1.0)
    else:
        return _joint_to_mi(joint=_np.ascontiguousarray(joint), forward_euler_a=1.0)


def MI_continuous_continuous(a,
                             b,
                             bw_multiplier,
                             a_N=300,
                             b_N=300,
                             kernel="epa",
                             bw="silverman",
                             norm=2,
                             **kwarg):
    """MI between two continuous variables."""
    # Filter out NaN values
    valid_mask = ~(_np.isnan(a) | _np.isnan(b))
    a_clean = a[valid_mask]
    b_clean = b[valid_mask]
    
    sorted_indices = _np.argsort(a_clean)
    data = _np.vstack((a_clean[sorted_indices], b_clean[sorted_indices])).T
    _data = _scaler().fit_transform(data)

    bw1, bw2 = _bivariate_bw(_data, bw_multiplier, bw)
    # Don't pass unexpected kwargs to FFTKDE
    grid, joint = _FFTKDE(kernel=kernel, norm=norm).fit(_data).evaluate((a_N, b_N))
    joint = joint.reshape(b_N, -1).T
    joint[joint < 0] = 0

    a_step, b_step = grid[b_N, 0] - grid[0, 0], grid[1, 1] - grid[0, 1]
    if CYTHON_AVAILABLE:
        return joint_to_mi_cython(joint=_np.ascontiguousarray(joint),
                                  forward_euler_a=a_step,
                                  forward_euler_b=b_step)
    else:
        return _joint_to_mi(joint=_np.ascontiguousarray(joint),
                           forward_euler_a=a_step,
                           forward_euler_b=b_step)


def MI_binary_continuous(a,
                         b,
                         bw_multiplier,
                         N=500,
                         kernel="epa",
                         bw="silverman",
                         **kwarg):
    """MI between binary and continuous variables."""
    # For binary outcomes, use binning approach for consistency
    # The KDE approach has bandwidth selection issues for well-separated binary outcomes
    return _binning_MI_discrete(a, b)


# Conversion utilities

def Pearson_to_MI_Gaussian(corr):
    """Convert Pearson correlation to MI (Gaussian assumption)."""
    if CYTHON_AVAILABLE:
        return Pearson_to_MI_Gaussian_cython(corr)
    else:
        if corr == -1 or corr == 1:
            return _np.inf
        return -0.5 * (_np.log1p(-corr**2))


def MI_to_Linfoot(mi):
    """Convert MI to Linfoot's measure."""
    if CYTHON_AVAILABLE:
        return MI_to_Linfoot_cython(mi)
    else:
        if mi < 0:
            raise ValueError("Mutual information cannot be negative.")
        return (1. - _np.exp(-2. * mi))**0.5