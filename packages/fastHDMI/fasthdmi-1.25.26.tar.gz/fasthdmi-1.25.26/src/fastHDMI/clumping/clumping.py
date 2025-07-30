#!/usr/bin/env python
# coding: utf-8

"""MI-based clumping."""

import numpy as _np
import multiprocess as _mp
from tqdm import tqdm as _tqdm
from bed_reader import open_bed as _open_bed

from ..utils import Pearson_to_MI_Gaussian
from ..mi_estimation import MI_012_012
from ..screening import continuous_screening_csv_parallel, continuous_screening_dataframe_parallel
from ..io import _read_csv


def clump_plink_parallel(bed_file,
                         bim_file,
                         fam_file,
                         clumping_threshold=Pearson_to_MI_Gaussian(.6),
                         num_SNPS_exam=_np.inf,
                         core_num="NOT DECLARED",
                         multp=10,
                         verbose=1):
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
    bed1_sid = _np.array(list(bed1.sid))
    if num_SNPS_exam == _np.inf:
        num_SNPS_exam = len(bed1_sid) - 1
    keep_cols = _np.arange(
        len(bed1_sid))  # pruning by keeping all SNPS at the beginning
    _iter = _np.arange(num_SNPS_exam)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    for current_var_ind in _iter:  # note that here _iter and keep_cols don't need to agree, by the break command comes later
        if current_var_ind + 1 <= len(keep_cols):
            outcome = bed1.read(_np.s_[:, current_var_ind],
                                dtype=_np.int8).flatten()
            gene_ind = _np.where(outcome != -127)
            outcome = outcome[gene_ind]

            def _012_012_plink_slice(_slice):

                def _map_foo(j):
                    _SNP = bed1.read(_np.s_[:, j], dtype=_np.int8).flatten()
                    _SNP = _SNP[gene_ind]  # get gene iid also in outcome iid
                    _outcome = outcome[_SNP !=
                                       -127]  # remove missing SNP in outcome
                    _SNP = _SNP[_SNP != -127]  # remove missing SNP
                    return MI_012_012(a=_outcome, b=_SNP)

                _MI_slice = _np.array(list(map(_map_foo, _slice)))
                return _MI_slice

            # multiprocessing starts here
            ind = keep_cols[current_var_ind + 1:]
            __iter = _np.array_split(ind, core_num * multp)
            with _mp.Pool(core_num) as pl:
                MI_UKBB = pl.map(_012_012_plink_slice, __iter)
            MI_UKBB = _np.hstack(MI_UKBB)
            keep_cols = _np.hstack(
                (keep_cols[:current_var_ind + 1],
                 keep_cols[current_var_ind +
                           1:][MI_UKBB <= clumping_threshold]))
        else:
            break
    return current_var_ind, bed1_sid[keep_cols]


def clump_continuous_csv_parallel(
        csv_file="_",
        _usecols=[],
        a_N=300,
        b_N=300,
        kernel="epa",
        bw="silverman",
        bw_multiplier=1.,
        norm=2,
        clumping_threshold=Pearson_to_MI_Gaussian(.6),
        num_vars_exam=_np.inf,
        core_num="NOT DECLARED",
        multp=10,
        csv_engine="c",
        parquet_file="_",
        sample=256000,
        verbose=1,
        share_memory=True,
        **kwarg):
    """
    Perform clumping based on mutual information thresholding
    The clumping process starts from the left to right, preserve input variables under the clumping threshold
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.    """
    # initialization
    _, keep_cols = _read_csv(csv_file=csv_file,
                             _usecols=_usecols,
                             csv_engine="dask",
                             parquet_file=parquet_file,
                             sample=sample,
                             verbose=verbose)

    del _

    if num_vars_exam == _np.inf:
        num_vars_exam = len(keep_cols) - 1
    _iter = _np.arange(num_vars_exam)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    for current_var_ind in _iter:  # note that here _iter and keep_cols don't need to agree, by the break command comes later
        if current_var_ind + 1 <= len(keep_cols):
            _MI = continuous_screening_csv_parallel(
                csv_file=csv_file,
                _usecols=keep_cols[current_var_ind:],
                kernel=kernel,
                bw=bw,
                bw_multiplier=bw_multiplier,
                norm=norm,
                core_num=core_num,
                multp=multp,
                csv_engine=csv_engine,
                parquet_file=parquet_file,
                sample=sample,
                verbose=0,
                share_memory=share_memory,
                **kwarg)
            # current_var_ind + 1 since the current variable will be included anyway
            keep_cols = _np.hstack(
                (keep_cols[:current_var_ind + 1],
                 keep_cols[current_var_ind + 1:][_MI <= clumping_threshold]))
        else:
            break
    return current_var_ind, keep_cols


def clump_continuous_dataframe_parallel(
        dataframe="_",
        _usecols=[],
        a_N=300,
        b_N=300,
        kernel="epa",
        bw="silverman",
        bw_multiplier=1.,
        norm=2,
        clumping_threshold=Pearson_to_MI_Gaussian(.6),
        num_vars_exam=_np.inf,
        core_num="NOT DECLARED",
        multp=10,
        csv_engine="c",
        verbose=1,
        share_memory=True,
        **kwarg):
    """
    Perform clumping based on mutual information thresholding
    The clumping process starts from the left to right, preserve input variables under the clumping threshold
    share_memory is to indicate whether to share the dataframe in memory to 
    multiple processes -- if set to False, each process will copy the entire dataframe respectively. However, 
    to read very large dataframe using dask, this option should usually be turned off.    """
    # initialization
    _df = dataframe
    if _np.array(_usecols).size == 0:
        keep_cols = _np.array(_df.columns.to_list()[1:])
    else:
        keep_cols = _np.array(_usecols)

    if num_vars_exam == _np.inf:
        num_vars_exam = len(keep_cols) - 1
    _iter = _np.arange(num_vars_exam)
    if verbose >= 1:
        _iter = _tqdm(_iter)
    for current_var_ind in _iter:  # note that here _iter and keep_cols don't need to agree, by the break command comes later
        if current_var_ind + 1 <= len(keep_cols):
            _MI = continuous_screening_dataframe_parallel(
                dataframe=dataframe,
                _usecols=keep_cols[current_var_ind:],
                kernel=kernel,
                bw=bw,
                bw_multiplier=bw_multiplier,
                norm=norm,
                core_num=core_num,
                multp=multp,
                csv_engine=csv_engine,
                verbose=0,
                share_memory=share_memory,
                **kwarg)
            # current_var_ind + 1 since the current variable will be included anyway
            keep_cols = _np.hstack(
                (keep_cols[:current_var_ind + 1],
                 keep_cols[current_var_ind + 1:][_MI <= clumping_threshold]))
        else:
            break
    return current_var_ind, keep_cols