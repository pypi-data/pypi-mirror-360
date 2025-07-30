""" Utility functions for use through PISCES
"""
import numpy as np
import polars as pl

from pisces.constants import (
    MOD_SEQ_KEY, SOURCE_KEY, SCAN_KEY,
)

def combine_list(list_of_strs):
    """ Function to convert a list of 
    """
    final_list = []
    for prots in list_of_strs:
        add_prots = [x for x in prots.split(' ') if x]
        final_list.extend(add_prots)
    return list(set(final_list))

def divide_df(df, n_cores):
    """ Split up DataFrame for parallel execution.
    """
    batch_size = df.shape[0]//n_cores
    batch_values = []
    for batch_idx in range(n_cores):
        batch_values.extend([batch_idx]*batch_size)

    if (additional_psms := df.shape[0]%n_cores):
        batch_values.extend([n_cores-1]*additional_psms)

    df = df.with_columns(
        pl.Series(name='batch', values=batch_values)
    )
    return df.partition_by('batch')

def format_for_perc(canonical_id_df, nc_df, output_folder):
    """ Function to format PISCES output similarly to percolator PSMs.
    """
    all_ids = []
    for strat_idx, id_df in enumerate([canonical_id_df, nc_df]):
        if id_df is None:
            continue
        if not strat_idx:
            q_val_col = 'qValue'
            score_col = 'piscesScore1'
            prot_code = 'can'
        else:
            q_val_col = 'qValue_PSM'
            score_col = 'piscesScore'
            prot_code = 'nc'

        id_df = id_df.with_columns(
            pl.struct(['source', 'scan', 'modifiedSequence']).map_elements(
                lambda df_row : f'{df_row["source"]}_{df_row["scan"]}_{df_row["modifiedSequence"]}',
                return_dtype=pl.String
            ).alias('PSMId'),
            pl.lit(prot_code).alias('proteinIds'),
        )
        id_df = id_df.rename({
            score_col: 'score',
            q_val_col: 'q-value',
        })
        id_df = id_df.select(['PSMId', 'score', 'q-value', 'peptide', 'proteinIds'])
        all_ids.append(id_df)

    total_df = pl.concat(all_ids)
    total_df = total_df.sort(
        by=['q-value', 'score', 'PSMId'],
        descending=[True, True, False],
    )

    total_df.write_csv(
        f'{output_folder}/final_percolator_style.tab', separator='\t',
    )


def modify_columns(psm_df, required_schema, cols):
    """ Function ensure all columns to be concatenated have the same schema.
    """
    psm_df = psm_df.with_columns(pl.lit(1).alias('mutated'))
    psm_df = psm_df.select(cols)
    for col, dtype in psm_df.schema.items():
        if dtype != required_schema[col]:
            psm_df = psm_df.with_columns(pl.col(col).cast(required_schema[col]))

    return psm_df


def split_psm_ids(psm_id):
    """ Function for splitting a PSM Id back into its source name, scan number
        and peptide sequence.

    Parameters
    ----------
    df_row : pd.Series
        A row of the DataFrame to which the function is being applied.

    Parameters
    ----------
    df_row : pd.Series
        The same row with source and scan added.
    """
    results = {}
    source_scan_list = psm_id.split('_')
    results[MOD_SEQ_KEY] = source_scan_list[-1]
    results[SCAN_KEY] = int(source_scan_list[-2])
    results[SOURCE_KEY] = '_'.join(source_scan_list[:-2])
    return results


def bounded_sigmoid(prior_prob, steepness, crossing_point):
    """ Function to map [0, 1] on [0, 1] with possible sigmoidal shape.

    Parameters
    ----------
    prior_prob : float
        Prior probability in range [0, 1].
    """
    return 1/(1+(prior_prob**(np.log(2)/np.log(crossing_point))-1)**steepness)


def calc_likelihood(label, pisces_prob, steepness, crossing_point):
    """ Function to adjust likelihoods
    """
    new_prob = bounded_sigmoid(pisces_prob, steepness, crossing_point)

    if not label:
        return -np.log(1 - new_prob)

    return -np.log(new_prob)


def total_likelihood(params, pisces_basic_likes):
    """ Function to calculate the sum of the log likelihoods across all observations.
    """
    return pisces_basic_likes.apply(
        lambda x, stp=params[0], cp=params[1] : calc_likelihood(
            x['correct'], x['piscesScore'], stp, cp
        ),
        axis=1,
    ).sum()
