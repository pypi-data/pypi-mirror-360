#!/usr/bin/env python
# coding: utf-8

"""I/O utilities."""

import numpy as _np
import pandas as _pd
import dask.dataframe as _dd


def _read_csv(csv_file, _usecols, csv_engine, parquet_file, sample, verbose=1):
    """
    Read a csv file using differnet engines. Use dask to read csv if low in memory.
    """
    assert csv_engine in [
        "dask", "pyarrow", "fastparquet", "c", "python"
    ], "Only dask and pandas csv engines or fastparquet are supported to read csv files."
    if _np.array(_usecols).size == 0:
        if verbose > 1:
            print(
                "Variable names not provided -- start reading variable names from csv file now, might take some time, depending on the csv file size."
            )
        if csv_engine == "dask":
            _df = _dd.read_csv(csv_file, sample=sample)
            _usecols = _np.array(list(_df.columns))
        elif csv_engine in ["pyarrow", "c",
                            "python"]:  # these are pandas CSV engines
            _df = _pd.read_csv(csv_file,
                               encoding='unicode_escape',
                               engine=csv_engine)
            _usecols = _np.array(_df.columns.to_list())
        elif csv_engine == "fastparquet":
            _df = _pd.read_parquet(parquet_file, engine="fastparquet")
            _usecols = _np.array(_df.columns.to_list())
        if verbose > 1:
            print("Reading variable names from csv file finished.")
    else:
        _usecols = _np.array(_usecols)
        if csv_engine == "dask":
            _df = _dd.read_csv(csv_file, names=_usecols, sample=sample)
        elif csv_engine in ["pyarrow", "c", "python"]:
            _df = _pd.read_csv(csv_file,
                               encoding='unicode_escape',
                               usecols=_usecols,
                               engine=csv_engine)
        elif csv_engine == "fastparquet":
            _df = _pd.read_parquet(parquet_file,
                                   engine="fastparquet")[_usecols]
    return _df, _usecols


def _read_two_columns(_df, __, csv_engine):
    """
    Read two columns from a dataframe object, remove NaN. Use dask to read csv if low in memory.
    """
    if csv_engine == "dask":
        _ = _np.asarray(_df[__].dropna().compute())
    elif csv_engine in ["pyarrow", "c", "python",
                        "fastparquet"]:  # these are engines using pandas
        _ = _df[__].dropna().to_numpy()

    _a = _[:, 0].copy()  # such that _df won't be mutated
    _b = _[:, 1].copy()  # such that _df won't be mutated
    return _a, _b