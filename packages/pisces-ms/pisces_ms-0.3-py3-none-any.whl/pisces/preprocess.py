""" Functions for preprocessing de novo identifications
"""
import os

import polars as pl

from pisces.utils import split_psm_ids
from pisces.constants import (
    MOD_SEQ_KEY,
    PEPTIDE_KEY,
    SCAN_KEY,
    SOURCE_KEY,
)

FINAL_COLUMNS = [
    SOURCE_KEY,
    SCAN_KEY,
    PEPTIDE_KEY,
    MOD_SEQ_KEY,
    'piscesScore1',
]


def preprocess_de_novo_psms(config):
    """ Function to preprocess all de novo PSMs, scoring them against the canonical model.
    """
    # Read in de novo hits.
    holding_dir = f'{config.output_folder}/holdingFolder'
    all_feat_dfs = [x for x in os.listdir(holding_dir) if x.startswith('deNovo_pms_')]
    all_psms_df = pl.concat(
        [pl.read_csv(f'{holding_dir}/{feat_df}', separator='\t') for feat_df in all_feat_dfs]
    )

    # Score de novo hits.
    all_psms_df = all_psms_df.unique('specID')
    all_psms_df = apply_post_processing(all_psms_df)

    # Write to csv
    all_psms_df.write_csv(
        f'{config.output_folder}/all_scored_candidates.csv'
    )


def apply_post_processing(target_psms):
    """ Function to separate columns and re-add relevant information.
    """
    target_psms = target_psms.with_columns(
        pl.col('specID').map_elements(
            split_psm_ids, return_dtype=pl.Struct([
                pl.Field(MOD_SEQ_KEY, pl.String),
                pl.Field(SCAN_KEY, pl.Int64),
                pl.Field(SOURCE_KEY, pl.String),
            ])
        ).alias("results")
    ).unnest("results")

    target_psms = target_psms.with_columns(
        pl.col(PEPTIDE_KEY).map_elements(lambda x : x.split('.')[1], return_dtype=pl.String)
    )

    if 'isobarSource' in target_psms.columns:
        target_psms = target_psms.select(FINAL_COLUMNS +['isobarSource'])
    else:
        target_psms = target_psms.select(FINAL_COLUMNS)

    return target_psms.sort(
        by=['piscesScore1', SCAN_KEY, MOD_SEQ_KEY], descending=[True, False, False],
    )
