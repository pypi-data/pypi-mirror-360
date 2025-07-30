# fastHDMI - Fast High-Dimensional Mutual Information Estimation

## Kai Yang
### Contact: <kai.yang2 "at" mail.mcgill.ca>
### [GPG Public Key Fingerprint: B9F863A56220DBD56B91C3E835022A1A5941D810](https://keys.openpgp.org/vks/v1/by-fingerprint/B9F863A56220DBD56B91C3E835022A1A5941D810)

Fast mutual information estimation for high-dimensional data. See the paper: [***`fastHDMI`: Fast Mutual Information Estimation for High-Dimensional Data***](https://arxiv.org/abs/2410.10082).

## Installation

```bash
pip install fastHDMI
```

## Usage

### Basic MI Estimation
```python
import fastHDMI
import numpy as np

# Generate sample data
x = np.random.randn(1000)
y = x + 0.5 * np.random.randn(1000)

# Estimate MI between continuous variables
mi = fastHDMI.MI_continuous_continuous(x, y, bw_multiplier=1.0)
print(f"MI: {mi}")

# MI between binary and continuous
binary_y = (y > 0).astype(int)
mi_binary = fastHDMI.MI_binary_continuous(binary_y, x, bw_multiplier=1.0)
```

### Feature Screening
```python
# Screen features against continuous outcome
X = np.random.randn(100, 50)  # 100 samples, 50 features
y = X[:, 0] + 0.5 * X[:, 1] + np.random.randn(100) * 0.1

# Single-threaded screening
mi_scores = fastHDMI.continuous_screening_array(X, y)

# Parallel screening (faster for many features)
mi_scores_parallel = fastHDMI.continuous_screening_array_parallel(X, y, core_num=4)

# Find top features
top_features = np.argsort(mi_scores)[-10:]
print(f"Top 10 features: {top_features}")
```

### CSV File Screening
```python
# Screen features from CSV file (outcome in first column)
mi_scores = fastHDMI.continuous_screening_csv_parallel(
    "data.csv",
    core_num=4
)

# Using sklearn MI estimation
mi_scores_sk = fastHDMI.continuous_skMI_screening_csv_parallel(
    "data.csv", 
    n_neighbors=3,
    core_num=4
)

# Pearson correlation screening
correlations = fastHDMI.Pearson_screening_csv_parallel(
    "data.csv",
    core_num=4
)
```

### DataFrame Screening
```python
import pandas as pd

# Create DataFrame with outcome as first column
df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(50)])
df.insert(0, 'outcome', y)

# Screen using DataFrame
mi_scores = fastHDMI.continuous_screening_dataframe(df)
```

## Package Information

- **PyPI**: [pypi.org/project/fastHDMI](https://pypi.org/project/fastHDMI/)

## ABIDE Data Analysis

- **Data**: [(pre-processed) ABIDE data](http://preprocessed-connectomes-project.org/abide/)
- **Notebook**: [/paper/ABIDE_data_analysis/ABIDE_analysis.ipynb](/paper/ABIDE_data_analysis/ABIDE_analysis.ipynb) - generates scripts for fastHDMI analysis
- **Execution**: Run scripts on server (e.g., Compute Canada), then rerun notebook with results (.npy files) to generate plots

## Computational Resources

- **Resource logs**: `seff-[jobID].out` files show job resource usage
- **Compute Canada docs**: [docs.alliancecan.ca/wiki/Running_jobs](https://docs.alliancecan.ca/wiki/Running_jobs)