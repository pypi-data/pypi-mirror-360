#!/usr/bin/env python
# coding: utf-8

"""Utility functions."""

import os
import numpy as _np
from numba import njit as _njit


def supports_avx2():
    """
    Check if the CPU supports AVX2 instructions.
    
    Returns:
        bool: True if AVX2 is supported, False otherwise.
    """
    # Using a simple way to check for AVX2 support
    return "avx2" in os.popen("cat /proc/cpuinfo").read()


def Pearson_to_MI_Gaussian(corr):
    """
    Convert Pearson correlation coefficient to mutual information for bivariate Gaussian variables.

    Parameters:
    corr (float): Pearson correlation coefficient.

    Returns:
    float: Mutual information.
    """
    if corr == -1 or corr == 1:
        return _np.inf
    return -0.5 * (_np.log1p(-corr**2))


def MI_to_Linfoot(mi):
    """
    Convert mutual information to Linfoot's measure of association.

    Parameters:
    mi (float): Mutual information.

    Returns:
    float: Linfoot's measure of association.
    """
    try:
        from ..cython_fun import MI_to_Linfoot_cython
        return MI_to_Linfoot_cython(mi)
    except ImportError:
        # Fallback
        if mi < 0:
            raise ValueError("Mutual information cannot be negative.")
        return (1. - _np.exp(-2. * mi))**0.5