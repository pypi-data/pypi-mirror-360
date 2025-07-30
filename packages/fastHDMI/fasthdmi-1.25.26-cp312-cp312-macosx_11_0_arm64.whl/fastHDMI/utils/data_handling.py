#!/usr/bin/env python
# coding: utf-8

"""Unified data handling utilities using pandas."""

import numpy as np
import pandas as pd
from typing import Union, Tuple, Optional, List


def ensure_dataframe(data: Union[pd.DataFrame, np.ndarray, str], 
                    outcome_column: Optional[str] = None,
                    feature_columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Convert input to DataFrame with outcome as first column."""
    # Convert to DataFrame if needed
    if isinstance(data, str):
        # Load from CSV
        df = pd.read_csv(data)
    elif isinstance(data, np.ndarray):
        # Convert numpy array to DataFrame
        if data.ndim == 1:
            df = pd.DataFrame(data, columns=['outcome'])
        else:
            n_cols = data.shape[1]
            columns = [f'feature_{i}' for i in range(n_cols)]
            df = pd.DataFrame(data, columns=columns)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")
    
    # Ensure outcome is first column
    if outcome_column is not None:
        if outcome_column not in df.columns:
            raise ValueError(f"Outcome column '{outcome_column}' not found in data")
        # Reorder columns with outcome first
        other_cols = [col for col in df.columns if col != outcome_column]
        df = df[[outcome_column] + other_cols]
    
    # Select feature columns if specified
    if feature_columns is not None:
        missing_cols = set(feature_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Feature columns not found: {missing_cols}")
        # Include outcome column (first) and specified features
        df = df[[df.columns[0]] + feature_columns]
    
    return df


def extract_X_y(df: pd.DataFrame, 
                outcome_index: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """Extract X and y from DataFrame. Outcome is at outcome_index (default 0)."""
    outcome_col = df.columns[outcome_index]
    feature_cols = [col for i, col in enumerate(df.columns) if i != outcome_index]
    
    y = df[outcome_col].values
    X = df[feature_cols].values
    
    return X, y


def standardize_screening_input(data: Union[pd.DataFrame, np.ndarray, str],
                               outcome: Optional[Union[np.ndarray, str]] = None,
                               outcome_type: str = 'continuous') -> Tuple[np.ndarray, np.ndarray]:
    """Standardize input for screening. Returns X, y arrays."""
    # Handle different input formats
    if isinstance(data, pd.DataFrame):
        if outcome is None:
            # Assume first column is outcome
            X, y = extract_X_y(data, outcome_index=0)
        elif isinstance(outcome, str):
            # outcome is a column name
            y = data[outcome].values
            X = data.drop(columns=[outcome]).values
        else:
            # outcome is array, data contains only features
            X = data.values
            y = np.asarray(outcome)
    elif isinstance(data, np.ndarray):
        if outcome is None:
            # Assume first column is outcome
            y = data[:, 0]
            X = data[:, 1:]
        else:
            X = data
            y = np.asarray(outcome)
    elif isinstance(data, str):
        # Load from file
        df = pd.read_csv(data)
        return standardize_screening_input(df, outcome, outcome_type)
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")
    
    # Validate outcome type
    if outcome_type == 'binary':
        unique_vals = np.unique(y[~np.isnan(y)])
        if not np.array_equal(unique_vals, [0, 1]) and not np.array_equal(unique_vals, [0]) and not np.array_equal(unique_vals, [1]):
            raise ValueError(f"Binary outcome should only contain 0 and 1, got {unique_vals}")
    elif outcome_type == '012':
        unique_vals = np.unique(y[~np.isnan(y)])
        if not all(val in [0, 1, 2] for val in unique_vals):
            raise ValueError(f"SNP outcome should only contain 0, 1, and 2, got {unique_vals}")
    
    return X, y


def prepare_screening_dataframe(df: pd.DataFrame, 
                               outcome_column: Optional[str] = None) -> pd.DataFrame:
    """
    Prepare DataFrame for screening by ensuring outcome is first column.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    outcome_column : str, optional
        Name of outcome column. If None, assumes first column.
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with outcome as first column
    """
    if outcome_column is not None:
        if outcome_column not in df.columns:
            raise ValueError(f"Outcome column '{outcome_column}' not found")
        # Reorder with outcome first
        other_cols = [col for col in df.columns if col != outcome_column]
        return df[[outcome_column] + other_cols]
    return df