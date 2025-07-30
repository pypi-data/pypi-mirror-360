"""Fast MI estimation for high-dimensional data."""

__version__ = "1.25.26"

from .mi_estimation import (
    MI_continuous_continuous,
    MI_binary_continuous,
    MI_continuous_012,
    MI_binary_012,
    MI_012_012,
    Pearson_to_MI_Gaussian,
    MI_to_Linfoot
)

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
    continuous_screening_plink_parallel,
    # Unified screening
    screen_features,
    rank_features
)


from .clumping import (
    clump_plink_parallel,
    clump_continuous_csv_parallel,
    clump_continuous_dataframe_parallel
)

from .utils import (
    supports_avx2,
    ensure_dataframe,
    extract_X_y,
    standardize_screening_input,
    prepare_screening_dataframe
)

__all__ = [
    # Version
    "__version__",
    # MI estimation
    "MI_continuous_continuous",
    "MI_binary_continuous",
    "MI_continuous_012",
    "MI_binary_012",
    "MI_012_012",
    "Pearson_to_MI_Gaussian",
    "MI_to_Linfoot",
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
    "continuous_screening_plink_parallel",
    # Clumping
    "clump_plink_parallel",
    "clump_continuous_csv_parallel",
    "clump_continuous_dataframe_parallel",
    # Utils
    "supports_avx2",
    # Unified screening
    "screen_features",
    "rank_features",
    # Data handling
    "ensure_dataframe",
    "extract_X_y",
    "standardize_screening_input",
    "prepare_screening_dataframe"
]