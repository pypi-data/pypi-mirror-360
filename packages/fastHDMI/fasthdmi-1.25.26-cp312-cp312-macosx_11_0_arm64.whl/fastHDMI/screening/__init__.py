"""Feature screening."""

from .screening import (
    # Array screening
    binary_screening_array,
    binary_screening_array_parallel,
    continuous_screening_array,
    continuous_screening_array_parallel,
    # CSV screening
    binary_screening_csv,
    binary_screening_csv_parallel,
    continuous_screening_csv,
    continuous_screening_csv_parallel,
    binning_binary_screening_csv_parallel,
    binning_continuous_screening_csv_parallel,
    binary_skMI_screening_csv_parallel,
    continuous_skMI_screening_csv_parallel,
    Pearson_screening_csv_parallel,
    # DataFrame screening
    binary_screening_dataframe,
    binary_screening_dataframe_parallel,
    continuous_screening_dataframe,
    continuous_screening_dataframe_parallel,
    binning_binary_screening_dataframe_parallel,
    binning_continuous_screening_dataframe_parallel,
    binary_skMI_screening_dataframe_parallel,
    continuous_skMI_screening_dataframe_parallel,
    Pearson_screening_dataframe_parallel,
    # PLINK screening
    binary_screening_plink,
    binary_screening_plink_parallel,
    continuous_screening_plink,
    continuous_screening_plink_parallel
)

__all__ = [
    # Array screening
    "binary_screening_array",
    "binary_screening_array_parallel",
    "continuous_screening_array",
    "continuous_screening_array_parallel",
    # CSV screening
    "binary_screening_csv",
    "binary_screening_csv_parallel",
    "continuous_screening_csv",
    "continuous_screening_csv_parallel",
    "binning_binary_screening_csv_parallel",
    "binning_continuous_screening_csv_parallel",
    "binary_skMI_screening_csv_parallel",
    "continuous_skMI_screening_csv_parallel",
    "Pearson_screening_csv_parallel",
    # DataFrame screening
    "binary_screening_dataframe",
    "binary_screening_dataframe_parallel",
    "continuous_screening_dataframe",
    "continuous_screening_dataframe_parallel",
    "binning_binary_screening_dataframe_parallel",
    "binning_continuous_screening_dataframe_parallel",
    "binary_skMI_screening_dataframe_parallel",
    "continuous_skMI_screening_dataframe_parallel",
    "Pearson_screening_dataframe_parallel",
    # PLINK screening
    "binary_screening_plink",
    "binary_screening_plink_parallel",
    "continuous_screening_plink",
    "continuous_screening_plink_parallel"
]

# Import unified screening functions
from .unified_screening import screen_features, rank_features

__all__.extend([
    "screen_features",
    "rank_features"
])