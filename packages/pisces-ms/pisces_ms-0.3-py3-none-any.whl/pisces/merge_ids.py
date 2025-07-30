""" Function to merge all identifications together.
"""
from inspire.input.casanovo import read_casanovo
from inspire.input.peaks_de_novo import read_peaks_de_novo
import polars as pl

from pisces.canonical_isobar import filter_canonical_isobars
from pisces.spectral_files import retrieve_charge
from pisces.utils import format_for_perc



QUANT_DF_COLS = [
    'source', 'scan', 'peptide', 'modifiedSequence', 'charge',
]
CANONICAL_FINAL_COLS = QUANT_DF_COLS + [
    'postErrProb', 'qValue', 'piscesScore1', 'piscesDiscoverable', 'tdDiscoverable',
]

def fetch_original_scores(filtered_df, config):
    if config.de_novo_method == 'casanovo':
        original_dn_df, _ = read_casanovo(
            config.de_novo_results, config.scans_folder,
            config.scans_format, retrieve_position_level=True,
        )
    else:
        original_dn_df, _ = read_peaks_de_novo(
            config.de_novo_results, retrieve_position_level=True,
        )
    original_dn_df = original_dn_df.unique(['source', 'scan', 'peptide', 'modifiedSequence'])
    filtered_df = filtered_df.join(
        original_dn_df,
        how='left',
        on=['source', 'scan', 'peptide', 'modifiedSequence'],
    )
    return filtered_df

def merge_identifications(config):
    """ Function to finalise PISCES outputs.
    """
    if config.db_search_results is None:
        fdr_estimated_df = pl.read_csv(f'{config.output_folder}/fdr_est_data.csv')
        format_for_perc(None, fdr_estimated_df, config.output_folder)
        return

    remapped_df = pl.read_csv(
        f'{config.output_folder}/mapped_candidates.csv'
    )

    filtered_df = filter_for_canonical_clash(remapped_df, config.output_folder)
    filtered_df = retrieve_charge(filtered_df, config.scans_folder)

    filtered_df = filter_canonical_isobars(config, filtered_df)

    filtered_df = fetch_original_scores(filtered_df, config)

    filtered_df.sort(
        ['adjustedProbability', 'peptide', 'scan'], descending=[True, False, False],
    ).write_csv(f'{config.output_folder}/filtered_mapped.csv')

    canonical_id_df, can_quant_df = combine_canonical_ids(filtered_df, config)
    quant_dfs = [can_quant_df]

    # Take non-canonical identifications
    nc_df = filtered_df.filter(
        pl.col('canonical_nProteins').eq(0)
    )

    # If columns not present fill with zeros and define stratum.
    for count_col in ['nContamProteins', 'nSpecific_ContamsProteins', 'nCrypticProteins']:
        if count_col not in nc_df.columns:
            nc_df = nc_df.with_columns(pl.lit(0).alias(count_col))

    for col_name in [
        'nSplicedProteins', 'nCrypticProteins',
        'nContamProteins', 'nSpecific_ContamsProteins',
    ]:
        if col_name not in nc_df.columns:
            nc_df = nc_df.with_columns(pl.lit(0).alias(col_name))
    nc_df = nc_df.with_columns(
        pl.struct([
            'nSplicedProteins', 'nCrypticProteins',
            'nContamProteins', 'nSpecific_ContamsProteins',
        ]).map_elements(
            define_type, return_dtype=pl.String,
        ).alias('Context')
    ).sort('qValue_PSM')

    # Write non-canonical DataFrame for plotting.
    nc_df.filter(pl.col('adjustedProbability').gt(config.p_val_cut_off)).select([
        'source', 'scan', 'peptide', 'modifiedSequence',
        'charge', 'Context', 'adjustedProbability'
    ]).unique('peptide').sort(
        ['adjustedProbability', 'peptide', 'scan'], descending=[True, False, False],
    ).write_csv(
        f'{config.output_folder}/deNovoOutput/plotData.csv'
    )

    if config.contaminants_folder is not None:
        contam_quant_df = finalise_outputs(nc_df, 'contaminants', config.output_folder)
        quant_dfs.append(contam_quant_df)
        nc_df = nc_df.filter(
            pl.col('nContamProteins').eq(0) &
            pl.col('nSpecific_ContamsProteins').eq(0)
        )

    if 'nCrypticProteins' in nc_df.columns:
        mm_quant_df = finalise_outputs(nc_df, 'multimapped', config.output_folder)
        spliced_quant_df = finalise_outputs(nc_df, 'spliced', config.output_folder)
        cryptic_quant_df = finalise_outputs(nc_df, 'cryptic', config.output_folder)
        unmapped_quant_df = finalise_outputs(nc_df, 'unmapped', config.output_folder)
        quant_dfs.extend([spliced_quant_df, mm_quant_df, cryptic_quant_df, unmapped_quant_df])
    else:
        spliced_quant_df = finalise_outputs(nc_df, 'spliced', config.output_folder)
        unmapped_quant_df = finalise_outputs(nc_df, 'unmapped', config.output_folder)
        quant_dfs.extend([spliced_quant_df, unmapped_quant_df])

    quant_df = pl.concat(quant_dfs)
    quant_df.write_csv(
        f'{config.output_folder}/deNovoOutput/peptidesForQuantification.csv'
    )
    format_for_perc(canonical_id_df, nc_df, config.output_folder)

    # Plot the PISCES non-canonical PSMs.
    config.run_inspire('De Novo', 'plotSpectra')
    config.move_pisces_file('deNovoOutput/spectralPlots.pdf', 'nonCanonicalPlots.pdf')

def filter_for_canonical_clash(remapped_df, output_folder):
    """ Function to remove PSMs 
    """
    canonical_id_df = pl.read_csv(
        f'{output_folder}/canonicalOutput/finalPsmAssignments.csv',
        columns=['source', 'scan', 'peptide', 'postErrProb'],
    )
    canonical_id_df = canonical_id_df.rename(
        {'peptide': 'canPeptide', 'postErrProb': 'canProb'}
    )

    filtered_remapped = remapped_df.join(
        canonical_id_df, how='left', on=['source', 'scan']
    )
    filtered_remapped = filtered_remapped.filter(
        pl.struct([
            'peptide', 'adjustedProbability', 'canPeptide', 'canProb',
        ]).map_elements(
            canonical_clash_psm_filter, return_dtype=pl.Boolean,
        )
    )
    filtered_remapped = filtered_remapped.drop(['canPeptide', 'canProb'])
    filtered_remapped = filtered_remapped.sort(by='adjustedProbability', descending=True)

    return filtered_remapped


def canonical_clash_psm_filter(df_row):
    """ Filter of PSMs if they have canonical clash.
    """
    # If there is no canonical candidate or we got the same peptide keep peptide.
    if not isinstance(df_row['canPeptide'], str) or (
        df_row['peptide'] == df_row['canPeptide'].replace('I', 'L')
    ):
        return True

    # If the canonical peptide is more probable or with PEP < 0.01 remove peptide.
    if (
        df_row['adjustedProbability'] < 1 - df_row['canProb'] or
        df_row['canProb'] < 0.01
    ):
        return False

    # Remaining case is PISCES peptide is more probable than canonical peptide.
    return True


def combine_canonical_ids(remapped_df, config):
    """ Function to combine canonical pisces identifiable and t/d identifiable
        psms.
    """
    # Get canonical discoverable by PISCES and apply cut off.
    canonical_remapped_df = remapped_df.filter(
        pl.col('canonical_nProteins').gt(0)
    )
    canonical_remapped_df = canonical_remapped_df.filter(
        pl.col('adjustedProbability').gt(config.p_val_cut_off)
    )
    canonical_remapped_df = canonical_remapped_df.with_columns(
        (1 - pl.col('adjustedProbability')).alias('postErrProb')
    )

    # Get canonical discoverable by t/d and apply cut off.
    canonical_id_df = pl.read_csv(
        f'{config.output_folder}/canonicalOutput/finalPsmAssignments.csv',
        columns=QUANT_DF_COLS + [
            'postErrProb', 'qValue', 'percolatorScore',
        ],
    )
    canonical_id_df = canonical_id_df.filter(pl.col('qValue') < 0.01).rename(
        {'percolatorScore': 'piscesScore1'},
    )
    print(canonical_id_df.shape, canonical_id_df['postErrProb'].mean())

    # Label t/d peptides as pisces discoverable or not:
    canonical_id_df = canonical_id_df.join(
        canonical_remapped_df.select(
            ['source', 'scan', 'peptide', 'postErrProb']
        ).rename(
            {'peptide': 'piscPeptide', 'postErrProb': 'piscesPostErrProb'}
        ),
        how='left',
        on=['source', 'scan'],
    )
    print(canonical_id_df.shape, canonical_id_df['postErrProb'].mean())
    canonical_id_df = canonical_id_df.with_columns(
        (
            pl.col('piscPeptide').eq(pl.col('peptide').str.replace_all('I', 'L')) &
            pl.col('piscPeptide').is_not_null()
        ).cast(pl.Int8).alias('piscesDiscoverable'),
        pl.lit(1).cast(pl.Int8).alias('tdDiscoverable'),
    )
    print(canonical_id_df.shape, canonical_id_df['piscesDiscoverable'].mean(), canonical_id_df['tdDiscoverable'].mean())
    # Filter any peptides where PISCES found a better match:
    canonical_id_df = canonical_id_df.filter(
        pl.col('piscPeptide').is_null() |
        pl.col('piscPeptide').eq(pl.col('peptide').str.replace_all('I', 'L')) |
        pl.col('postErrProb').lt(pl.col('piscesPostErrProb'))
    ).drop(['piscPeptide', 'piscesPostErrProb'])
    print(canonical_id_df.shape, canonical_id_df['piscesDiscoverable'].mean(), canonical_id_df['tdDiscoverable'].mean())

    # Prepare canonical id df for concatenation.
    canonical_remapped_df = canonical_remapped_df.with_columns(
        pl.lit(1).cast(pl.Int8).alias('piscesDiscoverable'),
        pl.lit(0).cast(pl.Int8).alias('tdDiscoverable'),
    )
    canonical_remapped_df = canonical_remapped_df.rename({
        'qValue_PSM': 'qValue',
    })

    # Concat and drop duplicates to keep td labeled peps.
    canonical_id_df = pl.concat([
        canonical_id_df.select(CANONICAL_FINAL_COLS),
        canonical_remapped_df.select(CANONICAL_FINAL_COLS),
    ])
    canonical_id_df = canonical_id_df.unique(
        subset=['source', 'scan']
    )
    canonical_id_df.write_csv(f'{config.output_folder}/final/canonical.csv')

    df_for_quant = canonical_id_df.select(QUANT_DF_COLS + ['piscesDiscoverable'])
    df_for_quant = df_for_quant.with_columns(
        pl.struct(['peptide', 'piscesDiscoverable']).map_elements(
            lambda df_row : (
                f'canonical_pisces_disc_{df_row["peptide"]}' if df_row['piscesDiscoverable'] == 1
                else f'canonical_td_only_{df_row["peptide"]}'
            ), return_dtype=pl.String,
        ).alias('proteins')
    )
    df_for_quant = df_for_quant.drop(['piscesDiscoverable'])

    return canonical_id_df, df_for_quant

def define_type(df_row):
    """ Function to define stratum of peptide.
    """
    if df_row['nContamProteins'] > 0 or df_row['nSpecific_ContamsProteins'] > 0:
        return 'contaminants'
    if df_row['nSplicedProteins'] > 0:
        if df_row['nCrypticProteins'] > 0:
            return 'multimapped'
        return 'spliced'
    if df_row['nCrypticProteins'] > 0:
        return 'cryptic'
    return 'unmapped'

def finalise_outputs(nc_df, code, output_folder):
    """ Function to write final PSM outputs and return DataFrame for quantification.
    """
    out_df = nc_df.filter(pl.col('Context').eq(code))
    out_df.write_csv(f'{output_folder}/final/{code}.csv')

    quant_df = out_df.select(QUANT_DF_COLS)
    quant_df = quant_df.with_columns(
        pl.col('peptide').map_elements(
            lambda x : f'{code}_{x}', return_dtype=pl.String
        ).alias('proteins')
    )
    return quant_df
