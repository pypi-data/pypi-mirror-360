#!/usr/bin/env python
# coding: utf-8

"""Unified screening functions with flexible input handling."""

import numpy as np
import pandas as pd
from typing import Union, Optional, List

from ..utils.data_handling import standardize_screening_input
from .screening import (
    continuous_screening_array,
    continuous_screening_array_parallel,
    binary_screening_array,
    binary_screening_array_parallel,
    continuous_screening_dataframe,
    continuous_screening_dataframe_parallel,
    binary_screening_dataframe,
    binary_screening_dataframe_parallel
)


def screen_features(data: Union[pd.DataFrame, np.ndarray, str],
                   outcome: Optional[Union[np.ndarray, str]] = None,
                   outcome_type: str = 'continuous',
                   method: str = 'mi',
                   parallel: bool = False,
                   core_num: Optional[int] = None,
                   **kwargs) -> np.ndarray:
    """
    Universal feature screening function with flexible input handling.
    
    Parameters:
    -----------
    data : pd.DataFrame, np.ndarray, or str
        Feature data. Can be:
        - DataFrame with features and outcome
        - Numpy array with features (and optionally outcome as first column)
        - Path to CSV file
    outcome : array-like or str, optional
        Outcome data or column name. If None, assumes first column is outcome.
    outcome_type : str
        Type of outcome: 'continuous', 'binary', or '012'
    method : str
        Screening method: 'mi' (mutual information), 'pearson', 'sklearn_mi', 'binning'
    parallel : bool
        Whether to use parallel processing
    core_num : int, optional
        Number of cores for parallel processing
    **kwargs : dict
        Additional arguments passed to screening functions
        
    Returns:
    --------
    scores : np.ndarray
        Feature importance scores
    """
    # Handle pandas DataFrame specially to use optimized functions
    if isinstance(data, pd.DataFrame) and outcome is None:
        # Use DataFrame screening functions directly
        if outcome_type == 'continuous':
            if parallel:
                scores = continuous_screening_dataframe_parallel(
                    data, core_num=core_num or 2, **kwargs
                )
            else:
                scores = continuous_screening_dataframe(data, **kwargs)
        elif outcome_type == 'binary':
            if parallel:
                scores = binary_screening_dataframe_parallel(
                    data, core_num=core_num or 2, **kwargs
                )
            else:
                scores = binary_screening_dataframe(data, **kwargs)
        else:
            # For 012, convert to array
            X, y = standardize_screening_input(data, outcome, outcome_type)
            scores = _screen_array(X, y, outcome_type, method, parallel, core_num, **kwargs)
    else:
        # Standardize input to arrays
        X, y = standardize_screening_input(data, outcome, outcome_type)
        scores = _screen_array(X, y, outcome_type, method, parallel, core_num, **kwargs)
    
    return scores


def _screen_array(X: np.ndarray, 
                 y: np.ndarray,
                 outcome_type: str,
                 method: str,
                 parallel: bool,
                 core_num: Optional[int],
                 **kwargs) -> np.ndarray:
    """Internal function to screen array data."""
    if outcome_type == 'continuous':
        if parallel:
            return continuous_screening_array_parallel(
                X, y, core_num=core_num or 2, **kwargs
            )
        else:
            return continuous_screening_array(X, y, **kwargs)
    elif outcome_type == 'binary':
        if parallel:
            return binary_screening_array_parallel(
                X, y, core_num=core_num or 2, **kwargs
            )
        else:
            return binary_screening_array(X, y, **kwargs)
    else:
        raise ValueError(f"Unsupported outcome type: {outcome_type}")


def rank_features(data: Union[pd.DataFrame, np.ndarray, str],
                 outcome: Optional[Union[np.ndarray, str]] = None,
                 outcome_type: str = 'continuous',
                 method: str = 'mi',
                 top_k: Optional[int] = None,
                 return_scores: bool = False,
                 **kwargs):
    """
    Rank features by importance and optionally return top-k.
    
    Parameters:
    -----------
    data : pd.DataFrame, np.ndarray, or str
        Feature data
    outcome : array-like or str, optional
        Outcome data or column name
    outcome_type : str
        Type of outcome
    method : str
        Screening method
    top_k : int, optional
        Number of top features to return
    return_scores : bool
        Whether to return scores along with rankings
    **kwargs : dict
        Additional arguments for screening
        
    Returns:
    --------
    rankings : np.ndarray
        Feature indices sorted by importance (descending)
    scores : np.ndarray, optional
        Feature scores (if return_scores=True)
    """
    scores = screen_features(data, outcome, outcome_type, method, **kwargs)
    rankings = np.argsort(scores)[::-1]
    
    if top_k is not None:
        rankings = rankings[:top_k]
    
    if return_scores:
        return rankings, scores[rankings]
    return rankings