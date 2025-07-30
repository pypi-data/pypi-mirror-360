""" Remap identified peptides to canonical and non-canonical strata.
"""
import os

import polars as pl

from pisces.constants import TREE_SIZE
from pisces.proteome_utils import distribute_mapping


def remap_to_proteome(config):
    """ Function to remap peptides to the spliced proteome.
    """
    # Take in final identifications and filter by FDR cut off and only take peptide column.
    fdr_estimated_df = pl.read_csv(f'{config.output_folder}/fdr_est_data.csv')
    fdr_estimated_df = fdr_estimated_df.with_columns(
        pl.col('source').cast(pl.String)
    )

    fdr_estimated_df = fdr_estimated_df.filter(
        pl.col('qValue_PSM').lt(0.2) & pl.col('adjustedProbability').gt(0.5)
    )

    unique_pep_df = fdr_estimated_df.select(['peptide']).unique()

    # Map to canonical and spliced strata.
    unique_pep_df = distribute_mapping(
        unique_pep_df,
        config.proteome,
        'canonical',
        config.n_cores,
        with_splicing=True,
        max_intervening=config.max_intervening,
        tree_size=config.tree_size,
    )

    # Map to contaminants and extract details
    if config.contaminants_folder is not None:
        unique_pep_df, _ = process_fasta_folder(
            unique_pep_df,
            config.contaminants_folder,
            config.n_cores,
            config.output_folder,
            'contam',
            tree_size=config.tree_size,
        )

    # Extract details for canonical and spliced
    unique_pep_df = extract_details(unique_pep_df, [], config.output_folder, 'canonical')
    unique_pep_df = extract_spliced_details(unique_pep_df, config.output_folder)

    # Map to cryptic strata and extract details
    if config.expanded_proteome_folder is not None:
        unique_pep_df, cryptic_strata = process_fasta_folder(
            unique_pep_df,
            config.expanded_proteome_folder,
            config.n_cores,
            config.output_folder,
            'cryptic',
            tree_size=config.tree_size,
        )
    else:
        cryptic_strata = []

    # Combine with the FDR estimated data.
    remapped_df = fdr_estimated_df.join(
        unique_pep_df,
        how='inner',
        on='peptide',
    )
    remapped_df = remapped_df.filter(
        pl.col('canonical_nProteins').gt(0) |
        (
            pl.col('modifiedSequence').str.contains('[+43.0]', literal=True).not_() &
            pl.col('modifiedSequence').str.contains('[+42.0]', literal=True).not_() &
            pl.col('modifiedSequence').str.contains('[+26.0]', literal=True).not_() &
            pl.col('modifiedSequence').str.contains('[-17.0]', literal=True).not_() &
            pl.col('modifiedSequence').str.contains('[+1.0]', literal=True).not_()
        )
    )
    remapped_df = remapped_df.sort(by=['qValue_PSM', 'peptide'])
    return remapped_df, cryptic_strata

def process_fasta_folder(
        peptide_id_df, fasta_folder, n_cores, output_folder, code, allow_can_mm=False, tree_size=TREE_SIZE,
    ):
    """ Function to add accessions for fasta files in a folder.
    """
    if code == 'contam' or allow_can_mm:
        mapping_df = peptide_id_df
    else:
        mapping_df = peptide_id_df.filter(pl.col('canonical_nProteins').eq(0))

    strata_names = []
    for proteome_file in os.listdir(fasta_folder):
        stratum_name = proteome_file.split('.fasta')[0]
        strata_names.append(stratum_name)

        mapped_df = distribute_mapping(
            mapping_df,
            f'{fasta_folder}/{proteome_file}',
            stratum_name,
            n_cores,
            tree_size=tree_size,
        )
        peptide_id_df = merge_to_main_df(
            peptide_id_df, mapped_df, stratum_name,
        )

    peptide_id_df = extract_details(
        peptide_id_df, strata_names,
        output_folder, code,
    )

    return peptide_id_df, strata_names


def merge_to_main_df(master_df, stratum_df, stratum_name):
    """ Function to merge mappings from a single stratum to the main peptide DataFrame.
    """
    master_df = master_df.join(
        stratum_df, on='peptide', how='left',
    )

    master_df = master_df.with_columns(
        pl.col(f'{stratum_name}_Proteins').fill_null('unknown').str.strip_chars()
    )
    master_df = master_df.with_columns(
        pl.col(f'{stratum_name}_nProteins').fill_null(0).cast(pl.Int64)
    )

    return master_df


def extract_details(unique_pep_df, strata_names, output_folder, code):
    """ Function to extract details on mappings a stratum or group of strata.
    """
    if strata_names:
        combined_col = f'n{code.title()}Proteins'
        count_cols = [f'{stratum}_nProteins' for stratum in strata_names]
        details_cols = [f'{stratum}_Proteins' for stratum in strata_names]

        # Sum total
        unique_pep_df = unique_pep_df.with_columns(
            pl.sum_horizontal(*count_cols).alias(combined_col)
        )
    else:
        combined_col = f'{code}_nProteins'
        count_cols = []
        details_cols = [f'{code}_Proteins']

    # Write details to csv
    unique_pep_df.filter(pl.col(combined_col).gt(0)).select(
        ['peptide', combined_col] + details_cols + count_cols
    ).unique('peptide').write_csv(
        f'{output_folder}/details/{code}.csv'
    )

    # Drop details columns
    unique_pep_df = unique_pep_df.drop(details_cols)

    return unique_pep_df


def extract_spliced_details(unique_pep_df, output_folder):
    """ Function to extract details of spliced peptide accessions.
    """
    unique_pep_df = unique_pep_df.unnest('splicedResults')
    spliced_unique_pep_df = unique_pep_df.filter(pl.col('nSplicedProteins') > 0)

    if 'nContamProteins' in spliced_unique_pep_df.columns:
        spliced_unique_pep_df = spliced_unique_pep_df.filter(pl.col('nContamProteins') == 0)

    spliced_unique_pep_df.select(
        'peptide', 'nSplicedProteins', 'sr1', 'interveningSeqLengths',
        'splicedProteins', 'sr1_Index', 'sr2_Index', 'isForward',
    ).write_csv(f'{output_folder}/details/spliced.csv')

    unique_pep_df = unique_pep_df.drop([
        'splicedProteins', 'sr1_Index', 'sr2_Index',
        'sr1', 'interveningSeqLengths', 'isForward',
    ])

    return unique_pep_df
