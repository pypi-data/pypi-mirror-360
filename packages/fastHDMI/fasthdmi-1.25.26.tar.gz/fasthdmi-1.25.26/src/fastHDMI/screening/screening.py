#!/usr/bin/env python
# coding: utf-8

"""Variable screening using MI."""

import warnings as _warnings
import multiprocess as _mp
import ctypes as _ctypes
from sklearn.feature_selection import mutual_info_regression as _mutual_info_regression
from sklearn.feature_selection import mutual_info_classif as _mutual_info_classif
from dask import dataframe as _dd
import pandas as _pd
import numpy as _np
from tqdm import tqdm as _tqdm
from bed_reader import open_bed as _open_bed

# Import MI functions from mi_estimation module
from ..mi_estimation import (
    MI_continuous_012,
    MI_binary_012,
    MI_continuous_continuous,
    MI_binary_continuous,
    Pearson_to_MI_Gaussian
)

# Import binning functions
import os

# Import supports_avx2 from utils
from ..utils import supports_avx2

# Import IO functions
from ..io import _read_csv, _read_two_columns

try:
    from ..cython_fun import binning_MI_cython, binning_MI_discrete_cython
except ImportError:
    # Fallback implementations if Cython module not available
    from ..mi_estimation import _binning_MI, _binning_MI_discrete
    binning_MI_cython = lambda a, b: _binning_MI(a, b)
    binning_MI_discrete_cython = lambda a, b: _binning_MI_discrete(a, b)

_warnings.filterwarnings('ignore')


# PLINK screening

# outcome_iid should be a  list of strings for identifiers
def continuous_screening_plink(bed_file,
                               bim_file,
                               fam_file,
                               outcome,
                               outcome_iid,
                               N=500,
                               kernel="epa",
                               bw="silverman",
                               bw_multiplier=1.,
                               verbose=1,
                               **kwarg):
    """
    (Single Core version) take plink files to calculate the mutual information between the continuous outcome and many SNP variables.
    """
    bed1 = _open_bed(filepath=bed_file,
                     fam_filepath=fam_file,
                     bim_filepath=bim_file)
    gene_iid = _np.array(list(bed1.iid))
    bed1_sid = _np.array(list(bed1.sid))
    outcome = outcome[_np.intersect1d(outcome_iid,
                                      gene_iid,
                                      assume_unique=True,
                                      return_indices=True)[1]]

    # get genetic indices
    gene_ind = _np.intersect1d(gene_iid,
                               outcome_iid,
                               assume_unique=True,
                               return_indices=True)[1]

    def _map_foo(j):
        _SNP = bed1.read(_np.s_[:, j], dtype=_np.int8).flatten()
        _SNP = _SNP[gene_ind]  # get gene iid also in outcome iid
        _outcome = outcome[_SNP != -127]  # remove missing SNP in outcome
        _SNP = _SNP[_SNP != -127]  # remove missing SNP
        return MI_continuous_012(a=_outcome,
                                 b=_SNP,
                                 N=N,
                                 kernel=kernel,
                                 bw=bw,
                                 bw_multiplier=bw_multiplier,
                                 **kwarg)

    _iter = range(len(bed1_sid))
    if verbose > 1:
        _iter = _tqdm(iter)
    MI_UKBB = _np.array(list(map(_map_foo, _iter)))
    return MI_UKBB


def binary_screening_plink(bed_file,
                           bim_file,
                           fam_file,
                           outcome,
                           outcome_iid,
                           verbose=1,
                           **kwarg):
    """
    (Single Core version) take plink files to calculate the mutual information between the binary outcome and many SNP variables.
    """
    bed1 = _open_bed(filepath=bed_file,
                     fam_filepath=fam_file,
                     bim_filepath=bim_file)
    gene_iid = _np.array(list(bed1.iid))
    bed1_sid = _np.array(list(bed1.sid))
    outcome = outcome[_np.intersect1d(outcome_iid,
                                      gene_iid,
                                      assume_unique=True,
                                      return_indices=True)[1]]
    # get genetic indices
    gene_ind = _np.intersect1d(gene_iid,
                               outcome_iid,
                               assume_unique=True,
                               return_indices=True)[1]

    def _map_foo(j):
        _SNP = bed1.read(_np.s_[:, j], dtype=_np.int8).flatten()
        _SNP = _SNP[gene_ind]  # get gene iid also in outcome iid
        _outcome = outcome[_SNP != -127]  # remove missing SNP in outcome
        _SNP = _SNP[_SNP != -127]  # remove missing SNP
        return MI_binary_012(a=_outcome, b=_SNP, **kwarg)

    _iter = range(len(bed1_sid))
    if verbose >= 1:
        _iter = _tqdm(_iter)
    MI_UKBB = _np.array(list(map(_map_foo, _iter)))
    return MI_UKBB


def continuous_screening_plink_parallel(bed_file,
                                        bim_file,
                                        fam_file,
                                        outcome,
                                        outcome_iid,
                                        N=500,
                                        kernel="epa",
                                        bw="silverman",
                                        bw_multiplier=1.,
                                        core_num="NOT DECLARED",
                                        multp=10,
                                        verbose=1,
                                        **kwarg):
    """
    (Multiprocessing version) take plink files to calculate the mutual information between the continuous outcome and many SNP variables.
    """
    # check some basic things
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    # read some metadata
    bed1 = _open_bed(filepath=bed_file,
                     fam_filepath=fam_file,
                     bim_filepath=bim_file)
    gene_iid = _np.array(list(bed1.iid))
    bed1_sid = _np.array(list(bed1.sid))
    outcome = outcome[_np.intersect1d(outcome_iid,
                                      gene_iid,
                                      assume_unique=True,
                                      return_indices=True)[1]]
    # get genetic indices
    gene_ind = _np.intersect1d(gene_iid,
                               outcome_iid,
                               assume_unique=True,
                               return_indices=True)[1]

    def _continuous_screening_plink_slice(_slice):

        def _map_foo(j):
            _SNP = bed1.read(_np.s_[:, j], dtype=_np.int8).flatten()
            _SNP = _SNP[gene_ind]  # get gene iid also in outcome iid
            _outcome = outcome[_SNP != -127]  # remove missing SNP in outcome
            _SNP = _SNP[_SNP != -127]  # remove missing SNP
            return MI_continuous_012(a=_outcome,
                                     b=_SNP,
                                     N=N,
                                     kernel=kernel,
                                     bw=bw,
                                     bw_multiplier=bw_multiplier,
                                     **kwarg)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(len(bed1_sid))
    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_UKBB = pl.map(_continuous_screening_plink_slice, _iter)
    MI_UKBB = _np.hstack(MI_UKBB)
    return MI_UKBB


def binary_screening_plink_parallel(bed_file,
                                    bim_file,
                                    fam_file,
                                    outcome,
                                    outcome_iid,
                                    core_num="NOT DECLARED",
                                    multp=10,
                                    verbose=1,
                                    **kwarg):
    """
    (Multiprocessing version) take plink files to calculate the mutual information between the binary outcome and many SNP variables.
    """
    # check basic things
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    # read some metadata
    bed1 = _open_bed(filepath=bed_file,
                     fam_filepath=fam_file,
                     bim_filepath=bim_file)
    gene_iid = _np.array(list(bed1.iid))
    bed1_sid = _np.array(list(bed1.sid))
    outcome = outcome[_np.intersect1d(outcome_iid,
                                      gene_iid,
                                      assume_unique=True,
                                      return_indices=True)[1]]
    # get genetic indices
    gene_ind = _np.intersect1d(gene_iid,
                               outcome_iid,
                               assume_unique=True,
                               return_indices=True)[1]

    def _binary_screening_plink_slice(_slice):

        def _map_foo(j):
            _SNP = bed1.read(_np.s_[:, j], dtype=_np.int8).flatten()
            _SNP = _SNP[gene_ind]  # get gene iid also in outcome iid
            _outcome = outcome[_SNP != -127]  # remove missing SNP in outcome
            _SNP = _SNP[_SNP != -127]  # remove missing SNP
            return MI_binary_012(a=_outcome, b=_SNP, **kwarg)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(len(bed1_sid))
    _iter = _np.array_split(ind, core_num * multp)
    if verbose > 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_UKBB = pl.map(_binary_screening_plink_slice, _iter)
    MI_UKBB = _np.hstack(MI_UKBB)
    return MI_UKBB


# CSV screening

def binary_screening_csv(csv_file="_",
                         _usecols=[],
                         N=500,
                         kernel="epa",
                         bw="silverman",
                         bw_multiplier=1.,
                         csv_engine="c",
                         parquet_file="_",
                         sample=256000,
                         verbose=1,
                         **kwarg):
    """
    Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    The outcome should be binary and the covariates be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    """
    assert csv_file != "_" or parquet_file != "_", "CSV or parquet filepath should be declared"
    # outcome is the first variable by default; if other specifications are needed, put it the first item in _usecols
    # read csv
    _df, _usecols = _read_csv(csv_file=csv_file,
                              _usecols=_usecols,
                              csv_engine=csv_engine,
                              parquet_file=parquet_file,
                              sample=sample,
                              verbose=verbose)

    def _map_foo(j):
        __ = [
            _usecols[0], _usecols[j + 1]
        ]  # here using _usecol[j + 1] because the left first column is the outcome
        _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
        return MI_binary_continuous(a=_a,
                                    b=_b,
                                    N=N,
                                    kernel=kernel,
                                    bw=bw,
                                    bw_multiplier=bw_multiplier,
                                    **kwarg)

    _iter = _np.arange(len(_usecols) - 1)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    MI_df = _np.array(list(map(_map_foo, _iter)))

    del _df

    return MI_df


def continuous_screening_csv(csv_file="_",
                             _usecols=[],
                             a_N=300,
                             b_N=300,
                             kernel="epa",
                             bw="silverman",
                             bw_multiplier=1.,
                             norm=2,
                             csv_engine="c",
                             parquet_file="_",
                             sample=256000,
                             verbose=1,
                             **kwarg):
    """
    Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    """
    assert csv_file != "_" or parquet_file != "_", "CSV or parquet filepath should be declared"
    # read csv
    _df, _usecols = _read_csv(csv_file=csv_file,
                              _usecols=_usecols,
                              csv_engine=csv_engine,
                              parquet_file=parquet_file,
                              sample=sample,
                              verbose=verbose)

    def _map_foo(j):
        __ = [
            _usecols[0], _usecols[j + 1]
        ]  # here using _usecol[j + 1] because the left first column is the outcome
        _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
        return MI_continuous_continuous(a=_a,
                                        b=_b,
                                        a_N=a_N,
                                        b_N=b_N,
                                        kernel=kernel,
                                        bw=bw,
                                        bw_multiplier=bw_multiplier,
                                        norm=norm,
                                        **kwarg)

    _iter = _np.arange(len(_usecols) - 1)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    MI_df = _np.array(list(map(_map_foo, _iter)))

    del _df

    return MI_df


def binary_screening_csv_parallel(csv_file="_",
                                  _usecols=[],
                                  N=500,
                                  kernel="epa",
                                  bw="silverman",
                                  bw_multiplier=1.,
                                  core_num="NOT DECLARED",
                                  multp=10,
                                  csv_engine="c",
                                  parquet_file="_",
                                  sample=256000,
                                  verbose=1,
                                  share_memory=True,
                                  **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    The outcome should be binary and the covariates be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    # check some basic things
    assert csv_file != "_" or parquet_file != "_", "CSV or parquet filepath should be declared"

    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    # read csv
    _df, _usecols = _read_csv(csv_file=csv_file,
                              _usecols=_usecols,
                              csv_engine=csv_engine,
                              parquet_file=parquet_file,
                              sample=sample,
                              verbose=verbose)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _binary_screening_csv_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return MI_binary_continuous(a=_a,
                                        b=_b,
                                        N=N,
                                        kernel=kernel,
                                        bw=bw,
                                        bw_multiplier=bw_multiplier,
                                        **kwarg)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here

    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome
    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_binary_screening_csv_slice, _iter)
    MI_df = _np.hstack(MI_df)

    del _df

    return MI_df


def continuous_screening_csv_parallel(csv_file="_",
                                      _usecols=[],
                                      a_N=300,
                                      b_N=300,
                                      kernel="epa",
                                      bw="silverman",
                                      bw_multiplier=1.,
                                      norm=2,
                                      core_num="NOT DECLARED",
                                      multp=10,
                                      csv_engine="c",
                                      parquet_file="_",
                                      sample=256000,
                                      verbose=1,
                                      share_memory=True,
                                      **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    # check some basic things
    assert csv_file != "_" or parquet_file != "_", "CSV or parquet filepath should be declared"

    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    # read csv
    _df, _usecols = _read_csv(csv_file=csv_file,
                              _usecols=_usecols,
                              csv_engine=csv_engine,
                              parquet_file=parquet_file,
                              sample=sample,
                              verbose=verbose)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _continuous_screening_csv_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return MI_continuous_continuous(a=_a,
                                            b=_b,
                                            a_N=a_N,
                                            b_N=b_N,
                                            kernel=kernel,
                                            bw=bw,
                                            bw_multiplier=bw_multiplier,
                                            norm=norm,
                                            **kwarg)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_continuous_screening_csv_slice, _iter)
    MI_df = _np.hstack(MI_df)

    del _df

    return MI_df


def binning_binary_screening_csv_parallel(csv_file="_",
                                          _usecols=[],
                                          core_num="NOT DECLARED",
                                          multp=10,
                                          csv_engine="c",
                                          parquet_file="_",
                                          sample=256000,
                                          verbose=1,
                                          share_memory=True,
                                          **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    The outcome should be binary and the covariates be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    # check some basic things
    assert csv_file != "_" or parquet_file != "_", "CSV or parquet filepath should be declared"

    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    # read csv
    _df, _usecols = _read_csv(csv_file=csv_file,
                              _usecols=_usecols,
                              csv_engine=csv_engine,
                              parquet_file=parquet_file,
                              sample=sample,
                              verbose=verbose)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _binary_screening_csv_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            _a = _a.astype(
                float
            )  # recall our binning_MI_discrete_cython doesn't accept int data type
            return binning_MI_discrete_cython(a=_a, b=_b)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here

    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome
    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_binary_screening_csv_slice, _iter)
    MI_df = _np.hstack(MI_df)

    del _df

    return MI_df


def binning_continuous_screening_csv_parallel(csv_file="_",
                                              _usecols=[],
                                              core_num="NOT DECLARED",
                                              multp=10,
                                              csv_engine="c",
                                              parquet_file="_",
                                              sample=256000,
                                              verbose=1,
                                              share_memory=True,
                                              **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    # check some basic things
    assert csv_file != "_" or parquet_file != "_", "CSV or parquet filepath should be declared"

    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    # read csv
    _df, _usecols = _read_csv(csv_file=csv_file,
                              _usecols=_usecols,
                              csv_engine=csv_engine,
                              parquet_file=parquet_file,
                              sample=sample,
                              verbose=verbose)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _continuous_screening_csv_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return binning_MI_cython(a=_a, b=_b)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_continuous_screening_csv_slice, _iter)
    MI_df = _np.hstack(MI_df)

    del _df

    return MI_df


def binary_skMI_screening_csv_parallel(csv_file="_",
                                       _usecols=[],
                                       n_neighbors=3,
                                       core_num="NOT DECLARED",
                                       multp=10,
                                       csv_engine="c",
                                       parquet_file="_",
                                       sample=256000,
                                       verbose=1,
                                       share_memory=True,
                                       **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be binary. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    # check some basic things
    assert csv_file != "_" or parquet_file != "_", "CSV or parquet filepath should be declared"

    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    # read csv
    _df, _usecols = _read_csv(csv_file=csv_file,
                              _usecols=_usecols,
                              csv_engine=csv_engine,
                              parquet_file=parquet_file,
                              sample=sample,
                              verbose=verbose)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _binary_skMI_df_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return _mutual_info_classif(y=_a.reshape(-1, 1),
                                        X=_b.reshape(-1, 1),
                                        n_neighbors=n_neighbors,
                                        discrete_features=False,
                                        **kwarg)[0]

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_binary_skMI_df_slice, _iter)
    MI_df = _np.hstack(MI_df)

    del _df

    return MI_df


def continuous_skMI_screening_csv_parallel(csv_file="_",
                                           _usecols=[],
                                           n_neighbors=3,
                                           core_num="NOT DECLARED",
                                           multp=10,
                                           csv_engine="c",
                                           parquet_file="_",
                                           sample=256000,
                                           verbose=1,
                                           share_memory=True,
                                           **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    # check some basic things
    assert csv_file != "_" or parquet_file != "_", "CSV or parquet filepath should be declared"

    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    # read csv
    _df, _usecols = _read_csv(csv_file=csv_file,
                              _usecols=_usecols,
                              csv_engine=csv_engine,
                              parquet_file=parquet_file,
                              sample=sample,
                              verbose=verbose)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _continuous_skMI_df_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return _mutual_info_regression(y=_a.reshape(-1, 1),
                                           X=_b.reshape(-1, 1),
                                           n_neighbors=n_neighbors,
                                           discrete_features=False,
                                           **kwarg)[0]

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_continuous_skMI_df_slice, _iter)
    MI_df = _np.hstack(MI_df)

    del _df

    return MI_df


def Pearson_screening_csv_parallel(csv_file="_",
                                   _usecols=[],
                                   core_num="NOT DECLARED",
                                   multp=10,
                                   csv_engine="c",
                                   parquet_file="_",
                                   sample=256000,
                                   verbose=1,
                                   share_memory=True):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the Pearson's correlation between outcome and covariates.
    If _usecols is given, the returned Pearson correlation will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    This function accounts for missing data better than the Pearson's correlation matrix function provided by numpy.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.    """
    # check some basic things
    assert csv_file != "_" or parquet_file != "_", "CSV or parquet filepath should be declared"

    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    # read csv
    _df, _usecols = _read_csv(csv_file=csv_file,
                              _usecols=_usecols,
                              csv_engine=csv_engine,
                              parquet_file=parquet_file,
                              sample=sample,
                              verbose=verbose)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _Pearson_screening_df_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return _np.corrcoef(_a, _b)[0, 1]

        _corr_slice = _np.array(list(map(_map_foo, _slice)))
        return _corr_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        corr_df = pl.map(_Pearson_screening_df_slice, _iter)
    corr_df = _np.hstack(corr_df)

    del _df

    return corr_df


# DataFrame screening

def binary_screening_dataframe(dataframe="_",
                               _usecols=[],
                               N=500,
                               kernel="epa",
                               bw="silverman",
                               bw_multiplier=1.,
                               csv_engine="c",
                               verbose=1,
                               **kwarg):
    """
    Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    The outcome should be binary and the covariates be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    """
    _df = dataframe
    if _np.array(_usecols).size == 0:
        _usecols = _np.array(_df.columns.to_list())
    else:
        _usecols = _np.array(_usecols)

    def _map_foo(j):
        __ = [
            _usecols[0], _usecols[j + 1]
        ]  # here using _usecol[j + 1] because the left first column is the outcome
        _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
        return MI_binary_continuous(a=_a,
                                    b=_b,
                                    N=N,
                                    kernel=kernel,
                                    bw=bw,
                                    bw_multiplier=bw_multiplier,
                                    **kwarg)

    _iter = _np.arange(len(_usecols) - 1)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    MI_df = _np.array(list(map(_map_foo, _iter)))

    return MI_df


def continuous_screening_dataframe(dataframe="_",
                                   _usecols=[],
                                   a_N=300,
                                   b_N=300,
                                   kernel="epa",
                                   bw="silverman",
                                   bw_multiplier=1.,
                                   norm=2,
                                   csv_engine="c",
                                   verbose=1,
                                   **kwarg):
    """
    Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    """
    _df = dataframe
    if _np.array(_usecols).size == 0:
        _usecols = _np.array(_df.columns.to_list())
    else:
        _usecols = _np.array(_usecols)

    def _map_foo(j):
        __ = [
            _usecols[0], _usecols[j + 1]
        ]  # here using _usecol[j + 1] because the left first column is the outcome
        _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
        return MI_continuous_continuous(a=_a,
                                        b=_b,
                                        a_N=a_N,
                                        b_N=b_N,
                                        kernel=kernel,
                                        bw=bw,
                                        bw_multiplier=bw_multiplier,
                                        norm=norm,
                                        **kwarg)

    _iter = _np.arange(len(_usecols) - 1)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    MI_df = _np.array(list(map(_map_foo, _iter)))

    return MI_df


def binary_screening_dataframe_parallel(dataframe="_",
                                        _usecols=[],
                                        N=500,
                                        kernel="epa",
                                        bw="silverman",
                                        bw_multiplier=1.,
                                        core_num="NOT DECLARED",
                                        multp=10,
                                        csv_engine="c",
                                        verbose=1,
                                        share_memory=True,
                                        **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    The outcome should be binary and the covariates be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    _df = dataframe
    if _np.array(_usecols).size == 0:
        _usecols = _np.array(_df.columns.to_list())
    else:
        _usecols = _np.array(_usecols)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _binary_screening_csv_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return MI_binary_continuous(a=_a,
                                        b=_b,
                                        N=N,
                                        kernel=kernel,
                                        bw=bw,
                                        bw_multiplier=bw_multiplier,
                                        **kwarg)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here

    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome
    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_binary_screening_csv_slice, _iter)
    MI_df = _np.hstack(MI_df)

    return MI_df


def continuous_screening_dataframe_parallel(dataframe="_",
                                            _usecols=[],
                                            a_N=300,
                                            b_N=300,
                                            kernel="epa",
                                            bw="silverman",
                                            bw_multiplier=1.,
                                            norm=2,
                                            core_num="NOT DECLARED",
                                            multp=10,
                                            csv_engine="c",
                                            verbose=1,
                                            share_memory=True,
                                            **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    _df = dataframe
    if _np.array(_usecols).size == 0:
        _usecols = _np.array(_df.columns.to_list())
    else:
        _usecols = _np.array(_usecols)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _continuous_screening_csv_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return MI_continuous_continuous(a=_a,
                                            b=_b,
                                            a_N=a_N,
                                            b_N=b_N,
                                            kernel=kernel,
                                            bw=bw,
                                            bw_multiplier=bw_multiplier,
                                            norm=norm,
                                            **kwarg)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_continuous_screening_csv_slice, _iter)
    MI_df = _np.hstack(MI_df)

    return MI_df


def binning_binary_screening_dataframe_parallel(dataframe="_",
                                                _usecols=[],
                                                core_num="NOT DECLARED",
                                                multp=10,
                                                csv_engine="c",
                                                verbose=1,
                                                share_memory=True,
                                                **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    The outcome should be binary and the covariates be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    _df = dataframe
    if _np.array(_usecols).size == 0:
        _usecols = _np.array(_df.columns.to_list())
    else:
        _usecols = _np.array(_usecols)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _binary_screening_csv_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return binning_MI_discrete_cython(a=_a, b=_b)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here

    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome
    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_binary_screening_csv_slice, _iter)
    MI_df = _np.hstack(MI_df)

    return MI_df


def binning_continuous_screening_dataframe_parallel(dataframe="_",
                                                    _usecols=[],
                                                    core_num="NOT DECLARED",
                                                    multp=10,
                                                    csv_engine="c",
                                                    verbose=1,
                                                    share_memory=True,
                                                    **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    _df = dataframe
    if _np.array(_usecols).size == 0:
        _usecols = _np.array(_df.columns.to_list())
    else:
        _usecols = _np.array(_usecols)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _continuous_screening_csv_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return binning_MI_cython(a=_a, b=_b)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_continuous_screening_csv_slice, _iter)
    MI_df = _np.hstack(MI_df)

    return MI_df


def binary_skMI_screening_dataframe_parallel(dataframe="_",
                                             _usecols=[],
                                             n_neighbors=3,
                                             core_num="NOT DECLARED",
                                             multp=10,
                                             csv_engine="c",
                                             verbose=1,
                                             share_memory=True,
                                             **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be binary. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    _df = dataframe
    if _np.array(_usecols).size == 0:
        _usecols = _np.array(_df.columns.to_list())
    else:
        _usecols = _np.array(_usecols)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _binary_skMI_df_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return _mutual_info_classif(y=_a.reshape(-1, 1),
                                        X=_b.reshape(-1, 1),
                                        n_neighbors=n_neighbors,
                                        discrete_features=False,
                                        **kwarg)[0]

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_binary_skMI_df_slice, _iter)
    MI_df = _np.hstack(MI_df)

    return MI_df


def continuous_skMI_screening_dataframe_parallel(dataframe="_",
                                                 _usecols=[],
                                                 n_neighbors=3,
                                                 core_num="NOT DECLARED",
                                                 multp=10,
                                                 csv_engine="c",
                                                 verbose=1,
                                                 share_memory=True,
                                                 **kwarg):
    """
    (Multiprocessing version) Take a (potentionally large) csv file to calculate the mutual information between outcome and covariates.
    Both the outcome and the covariates should be continuous. 
    If _usecols is given, the returned mutual information will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    _df = dataframe
    if _np.array(_usecols).size == 0:
        _usecols = _np.array(_df.columns.to_list())
    else:
        _usecols = _np.array(_usecols)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _continuous_skMI_df_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return _mutual_info_regression(y=_a.reshape(-1, 1),
                                           X=_b.reshape(-1, 1),
                                           n_neighbors=n_neighbors,
                                           discrete_features=False,
                                           **kwarg)[0]

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_df = pl.map(_continuous_skMI_df_slice, _iter)
    MI_df = _np.hstack(MI_df)

    return MI_df


def Pearson_screening_dataframe_parallel(dataframe="_",
                                         _usecols=[],
                                         core_num="NOT DECLARED",
                                         multp=10,
                                         csv_engine="c",
                                         verbose=1,
                                         share_memory=True):
    """
    (Multiprocessing version) Take a dataframe to calculate the Pearson's correlation between outcome and covariates.
    If _usecols is given, the returned Pearson correlation will match _usecols. 
    By default, the left first covariate should be the outcome -- use _usecols to adjust if not the case.
    This function accounts for missing data better than the Pearson's correlation matrix function provided by numpy.
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.
    """
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    _df = dataframe
    if _np.array(_usecols).size == 0:
        _usecols = _np.array(_df.columns.to_list())
    else:
        _usecols = _np.array(_usecols)

    # share_memory for multiprocess
    if share_memory == True:
        # the origingal dataframe is df, store the columns/dtypes pairs
        df_dtypes_dict = dict(list(zip(_df.columns, _df.dtypes)))
        # declare a shared Array with data from df
        mparr = _mp.Array(_ctypes.c_double, _df.values.reshape(-1))
        # create a new df based on the shared array
        _df = _pd.DataFrame(_np.frombuffer(mparr.get_obj()).reshape(_df.shape),
                            columns=_df.columns).astype(df_dtypes_dict)

    def _Pearson_screening_df_slice(_slice):

        def _map_foo(j):
            __ = [
                _usecols[0], _usecols[j]
            ]  # here using _usecol[j] because only input variables indices were splitted
            _a, _b = _read_two_columns(_df=_df, __=__, csv_engine=csv_engine)
            return _np.corrcoef(_a, _b)[0, 1]

        _corr_slice = _np.array(list(map(_map_foo, _slice)))
        return _corr_slice

    # multiprocessing starts here
    ind = _np.arange(
        1, len(_usecols)
    )  # starting from 1 because the first left column should be the outcome

    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        corr_df = pl.map(_Pearson_screening_df_slice, _iter)
    corr_df = _np.hstack(corr_df)

    return corr_df


# Array screening

def binary_screening_array(X,
                           y,
                           drop_na=True,
                           N=500,
                           kernel="epa",
                           bw="silverman",
                           bw_multiplier=1.,
                           verbose=1,
                           **kwarg):
    """
    Take a numpy file to calculate the mutual information between outcome and covariates.
    The outcome should be binary and the covariates be continuous. 
    If drop_na is set to be True, the NaN values will be dropped in a bivariate manner. 
    """

    def _map_foo(j):
        _a, _b = y.copy(), X[:, j].copy()
        if drop_na == True:
            _keep = _np.logical_not(
                _np.logical_or(_np.isnan(_a), _np.isnan(_b)))
            _a, _b = _a[_keep], _b[_keep]
        return MI_binary_continuous(a=_a,
                                    b=_b,
                                    N=N,
                                    kernel=kernel,
                                    bw=bw,
                                    bw_multiplier=bw_multiplier,
                                    **kwarg)

    _iter = _np.arange(X.shape[1])
    if verbose >= 1:
        _iter = _tqdm(_iter)
    MI_array = _np.array(list(map(_map_foo, _iter)))
    return MI_array


def continuous_screening_array(X,
                               y,
                               drop_na=True,
                               a_N=300,
                               b_N=300,
                               kernel="epa",
                               bw="silverman",
                               bw_multiplier=1.,
                               norm=2,
                               verbose=1,
                               **kwarg):
    """
    Take a numpy file to calculate the mutual information between outcome and covariates.
    The outcome should be continuous and the covariates be continuous. 
    If drop_na is set to be True, the NaN values will be dropped in a bivariate manner. 
    """

    def _map_foo(j):
        _a, _b = y.copy(), X[:, j].copy()
        if drop_na == True:
            _keep = _np.logical_not(
                _np.logical_or(_np.isnan(_a), _np.isnan(_b)))
            _a, _b = _a[_keep], _b[_keep]
        return MI_continuous_continuous(a=_a,
                                        b=_b,
                                        a_N=a_N,
                                        b_N=b_N,
                                        kernel=kernel,
                                        bw=bw,
                                        bw_multiplier=bw_multiplier,
                                        norm=norm,
                                        **kwarg)

    _iter = _np.arange(X.shape[1])
    if verbose >= 1:
        _iter = _tqdm(_iter)
    MI_array = _np.array(list(map(_map_foo, _iter)))
    return MI_array


def binary_screening_array_parallel(X,
                                    y,
                                    drop_na=True,
                                    N=500,
                                    kernel="epa",
                                    bw="silverman",
                                    bw_multiplier=1.,
                                    core_num="NOT DECLARED",
                                    multp=10,
                                    verbose=1,
                                    **kwarg):
    """
    (Multiprocessing version) Calculate the mutual information between outcome and covariates.
    The outcome should be binary and the covariates be continuous. 
    If drop_na is set to be True, the NaN values will be dropped in a bivariate manner. 
    """
    # check some basic things
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    def _binary_screening_array_slice(_slice):

        def _map_foo(j):
            _a, _b = y.copy(), X[:, j].copy()
            if drop_na == True:
                _keep = _np.logical_not(
                    _np.logical_or(_np.isnan(_a), _np.isnan(_b)))
                _a, _b = _a[_keep], _b[_keep]
            return MI_binary_continuous(a=_a,
                                        b=_b,
                                        N=N,
                                        kernel=kernel,
                                        bw=bw,
                                        bw_multiplier=bw_multiplier,
                                        **kwarg)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(
        X.shape[1]
    )  # starting from 1 because the first left column should be the outcome
    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_array = pl.map(_binary_screening_array_slice, _iter)
    MI_array = _np.hstack(MI_array)
    return MI_array


def continuous_screening_array_parallel(X,
                                        y,
                                        drop_na=True,
                                        a_N=300,
                                        b_N=300,
                                        kernel="epa",
                                        bw="silverman",
                                        bw_multiplier=1.,
                                        norm=2,
                                        core_num="NOT DECLARED",
                                        multp=10,
                                        verbose=1,
                                        **kwarg):
    """
    (Multiprocessing version) Calculate the mutual information between outcome and covariates.
    The outcome should be continuous and the covariates be continuous. 
    If drop_na is set to be True, the NaN values will be dropped in a bivariate manner. 
    """
    # check some basic things
    if core_num == "NOT DECLARED":
        core_num = _mp.cpu_count()
    else:
        assert core_num <= _mp.cpu_count(
        ), "Declared number of cores used for multiprocessing should not exceed number of cores on this machine."
    assert core_num >= 2, "Multiprocessing should not be used on single-core machines."

    def _continuous_screening_array_slice(_slice):

        def _map_foo(j):
            _a, _b = y.copy(), X[:, j].copy()
            if drop_na == True:
                _keep = _np.logical_not(
                    _np.logical_or(_np.isnan(_a), _np.isnan(_b)))
                _a, _b = _a[_keep], _b[_keep]
            return MI_continuous_continuous(a=_a,
                                            b=_b,
                                            a_N=a_N,
                                            b_N=b_N,
                                            kernel=kernel,
                                            bw=bw,
                                            bw_multiplier=bw_multiplier,
                                            norm=norm,
                                            **kwarg)

        _MI_slice = _np.array(list(map(_map_foo, _slice)))
        return _MI_slice

    # multiprocessing starts here
    ind = _np.arange(X.shape[1])
    _iter = _np.array_split(ind, core_num * multp)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    with _mp.Pool(core_num) as pl:
        MI_array = pl.map(_continuous_screening_array_slice, _iter)
    MI_array = _np.hstack(MI_array)
    return MI_array