""" Functions to create a report.
"""
import os

import pandas as pd

from pisces.plot_utils import (
    compare_to_baseline,
    create_basic_logo_plot,
    create_comparison_logo_plot,
    plot_assigned_psms,
    plot_cryptic_breakdown,
    plot_canonical_vs_nc,
    plot_lengths,
    plot_lengths_nc,
    plot_qc_figs,
)
from pisces.report.report_template import fill_pisces_report_template
from pisces.report.qc_report_template import fill_pisces_qc_report_template

def create_report(config):
    """ Function for creating a report into the features of different peptide strata.
    """
    compare_to_baseline(config)
    plot_assigned_psms(config.output_folder)
    create_motif_plots(config)
    plot_qc_figs(config)

    remapped_df = pd.read_csv(
        f'{config.output_folder}/filtered_mapped.csv',
    )
    if 'nContamProteins' not in remapped_df.columns:
        remapped_df['nContamProteins'] = 0
    if 'nCrypticProteins' not in remapped_df.columns:
        remapped_df['nCrypticProteins'] = 0
    if 'nSpecific_ContamsProteins' not in remapped_df.columns:
        remapped_df['nSpecific_ContamsProteins'] = 0
    remapped_df = remapped_df[[
        'peptide', 'canonical_nProteins', 'nSplicedProteins',
        'nContamProteins', 'nCrypticProteins', 'adjustedProbability',
        'nSpecific_ContamsProteins',
    ]]
    remapped_df = remapped_df[
        (remapped_df['adjustedProbability'] > config.p_val_cut_off)
    ]

    td_df = pd.read_csv(
        f'{config.output_folder}/canonicalOutput/finalPsmAssignments.csv'
    )
    td_df = td_df[td_df['qValue'] < 0.01]

    img_output = f'{config.output_folder}/img'

    if os.path.exists(f'{config.output_folder}/details/cryptic.csv'):
        cryptic_df = pd.read_csv(
            f'{config.output_folder}/details/cryptic.csv'
        )
        cryptic_cols = [
            'peptide', 'fiveUTR_nProteins', 'intergenic_nProteins',
            'CDS_frameshift_nProteins', 'threeUTR_nProteins', 'TrEMBL_nProteins',
            'lncRNA_nProteins', 'intronic_nProteins',
        ]
        if 'mutation_nProteins' in cryptic_df.columns:
            cryptic_cols.append('mutation_nProteins')
        if 'fusion_nProteins' in cryptic_df.columns:
            cryptic_cols.append('fusion_nProteins')
        cryptic_df = cryptic_df[cryptic_cols]
        plot_cryptic_breakdown(remapped_df, cryptic_df, img_output)

    plot_canonical_vs_nc(remapped_df, img_output)
    plot_lengths(remapped_df, td_df, img_output)
    plot_lengths_nc(remapped_df, img_output)

    fill_pisces_report_template(config)
    fill_pisces_qc_report_template(config)


def create_motif_plots(config):
    """ Functions to get motifs of different strata and differences betweeen strata.
    """
    canonical_id_df = pd.read_csv(
        f'{config.output_folder}/final/canonical.csv'
    )
    canonical_id_df = canonical_id_df[canonical_id_df['postErrProb'] < 1 - config.p_val_cut_off]
    canonical_id_df = canonical_id_df[canonical_id_df['peptide'].apply(lambda x : len(x) == 9)]

    canonical_id_df = canonical_id_df[canonical_id_df['piscesDiscoverable'] == 1]

    spliced_id_df = read_nc_stratum(config, 'spliced')
    multi_id_df = read_nc_stratum(config, 'multimapped')
    cryptic_id_df = read_nc_stratum(config, 'cryptic')

    create_basic_logo_plot(
        [
            canonical_id_df, spliced_id_df, multi_id_df, cryptic_id_df,
        ],
        [
            'Canonical', 'Spliced', 'Multi-Mapped', 'Cryptic',
        ],
        9,
        f'{config.output_folder}/img',
    )
    create_comparison_logo_plot(
        [spliced_id_df, cryptic_id_df, canonical_id_df,],
        ['Spliced', 'Cryptic', 'Canonical'],
        9,
        f'{config.output_folder}/img',
    )


def read_nc_stratum(config, stratum):
    """ Function read length 9 peptides identified.
    """
    id_df = pd.read_csv(
        f'{config.output_folder}/final/{stratum}.csv'
    )
    id_df = id_df[id_df['peptide'].apply(lambda x : len(x) == 9)]
    if id_df.shape[0] == 0:
        return None
    id_df = id_df[id_df['adjustedProbability'] > config.p_val_cut_off]
    return id_df
