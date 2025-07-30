""" Functions for finding canonical isobars to noncanonical PSMs.
"""
import polars as pl

from pisces.constants import MOD_SEQ_KEY, INSPIRE_PROCESSING_PIPELINES
from pisces.permute import permute_peptide
from pisces.preprocess import apply_post_processing
from pisces.proteome_utils import distribute_mapping

def get_canonical_scores(config):
    """ Function to scores for canonical peptides isobaric to de novo peptides.
    """
    final_psms_df = pl.read_csv(
        f'{config.output_folder}/canonicalOutput/finalPsmAssignments.csv',
        columns=['source', 'scan', 'peptide', 'modifiedSequence', 'charge', 'postErrProb'],
        dtypes=[pl.String, pl.Int64, pl.String,pl.String, pl.Int16, pl.Float64,],
    )

    final_psms_df = final_psms_df.filter(pl.col('postErrProb').lt(0.01))
    if final_psms_df.shape[0] > 2_000:
        final_psms_df = final_psms_df.sample(n=2_000, seed=42)
    final_psms_df.write_csv(f'{config.output_folder}/holdingFolder/isobarPsms.csv')

    config.remove_pisces_path('isobarOutput/mhcpan')
    config.remove_pisces_path('isobarOutput/formated_df.csv')

    for pipeline in INSPIRE_PROCESSING_PIPELINES:
        config.run_inspire('Isobar', pipeline)

    config.remove_pisces_path('isobarOutput/mhcpan')
    config.remove_pisces_path('isobarOutput/formated_df.csv')

    can_df = pl.read_csv(
        f'{config.output_folder}/isobarOutput/final_input.tab', separator='\t',
    )
    can_df = can_df.unique('specID')
    can_df = apply_post_processing(can_df)

    return can_df


def check_canonical_isobars(config, nc_df):
    """ Function to look for canonical isobars
    """
    nc_df = nc_df.with_columns(
        pl.col(MOD_SEQ_KEY).map_elements(
            lambda x : '_' + x.replace('[+42.0]', '') if '[+42.0]' in x else (
                '+' + x.replace('[+43.0]', '') if '[+43.0]' in x else (
                    '-' + x.replace('[-17.0]', '') if '[-17.0]' in x else (
                        '=' + x.replace('[+26.0]', '') if '[+26.0]' in x else x
                    )
                )
            ),
            return_dtype=pl.String,
        ).str.replace_many(
            ['M[+16.0]', 'C[+57.0]', 'N[+1.0]', 'Q[+1.0]', 'C[+119.0]'], ['m', 'c', 'n', 'q', 'y']
        ).alias('seqToPermute')
    )

    permutation_df = nc_df.with_columns(
        pl.col('seqToPermute').map_elements(
            permute_peptide, skip_nulls=False, return_dtype=pl.List(pl.String),
        ).alias('substitutePep'),
    ).explode('substitutePep')

    permutation_df = permutation_df.with_columns(
        pl.col('substitutePep').str.replace_many(
            ['m', 'c', 'n', 'q', '_', '+', '-', '=', 'y'],
            ['M', 'C', 'N', 'Q', '', '', '', '', 'C'],
        ).alias('peptide'),
        pl.col('substitutePep').str.replace_many(
            ['m', 'c', 'n', 'q', 'y'], ['M[+16.0]', 'C[+57.0]', 'N[+1.0]', 'Q[+1.0]', 'C[+119.0]']
        ).map_elements(
            lambda x : x[1] + '[+42.0]' + x[2:] if x.startswith('_') else (
                x[1] + '[+43.0]' + x[2:] if x.startswith('+') else (
                    x[1] + '[-17.0]' + x[2:] if x.startswith('-') else (
                        x[1] + '[+26.0]' + x[2:] if x.startswith('=') else x
                    )
                )
            ),
            return_dtype=pl.String,
        ).alias(MOD_SEQ_KEY),
    )

    if config.enzyme == 'trypsin':
        check_preceding = '*KR'
    else:
        check_preceding = None

    mapping_df = distribute_mapping(
        permutation_df, config.proteome, 'isobarCanonical', config.n_cores,
        filter_not_mapped=True, check_preceding=check_preceding,
    )
    isobar_can_df = permutation_df.select(
        ['source', 'scan', 'charge', 'peptide', 'modifiedSequence']
    ).join(
        mapping_df.select(['peptide']), on='peptide', how='inner',
    )
    isobar_can_df.write_csv(f'{config.output_folder}/holdingFolder/isobarPsms.csv')

    config.remove_pisces_path('isobarOutput/mhcpan')
    config.remove_pisces_path('isobarOutput/formated_df.csv')

    for pipeline in INSPIRE_PROCESSING_PIPELINES:
        config.run_inspire('Isobar', pipeline)

    config.remove_pisces_path('isobarOutput/mhcpan')
    config.remove_pisces_path('isobarOutput/formated_df.csv')

    config.move_pisces_file(
        'isobarOutput/final_input.tab',
        'holdingFolder/isobarPsms_processed.tab',
    )

    all_isobars_df = pl.read_csv(
        f'{config.output_folder}/holdingFolder/isobarPsms_processed.tab', separator='\t',
    )
    all_isobars_df = all_isobars_df.unique('specID')
    all_isobars_df = apply_post_processing(all_isobars_df)
    return all_isobars_df

def check_stratum(n_spliced_prot, n_cryp_prot):
    """ Function to check the stratum of a peptide.
    """
    if n_spliced_prot > 0:
        if n_cryp_prot > 0:
            return 'multi-mapped'
        return 'spliced'
    if n_cryp_prot > 0:
        return 'cryptic'
    return 'unmapped'

def filter_canonical_isobars(config, all_df):
    """ Function to filter peptides with high scoring canonical isobars.
    """
    can_df = get_canonical_scores(config)
    score_cut_off = can_df['piscesScore1'].quantile(config.can_iso_cut)

    if config.contaminants_folder is not None:
        can_contam_df = all_df.filter(
            pl.col('nSpecific_ContamsProteins').gt(0) |
            pl.col('nContamProteins').gt(0) |
            pl.col('canonical_nProteins').gt(0)
        )
        nc_df = all_df.filter(
            pl.col('nSpecific_ContamsProteins').eq(0) &
            pl.col('nContamProteins').eq(0) &
            pl.col('canonical_nProteins').eq(0)
        )
    else:
        can_contam_df = all_df.filter(
            pl.col('canonical_nProteins').gt(0)
        )
        nc_df = all_df.filter(
            pl.col('canonical_nProteins').eq(0)
        )

    if 'nCrypticProteins' in nc_df.columns:
        nc_df = nc_df.with_columns(
            pl.struct(['nSplicedProteins', 'nCrypticProteins']).map_elements(
                lambda x : check_stratum(x['nSplicedProteins'], x['nCrypticProteins']),
                return_dtype=pl.String,
            ).alias('stratum')
        )
    else:
        nc_df = nc_df.with_columns(pl.lit('non-canonical').alias('stratum'))

    isobar_df = check_canonical_isobars(config, nc_df)
    isobar_df = isobar_df.sort(by=['piscesScore1', 'peptide'], descending=[True, False])
    isobar_df = isobar_df.unique(subset=['source', 'scan'])
    isobar_df = isobar_df.rename({
        'peptide': 'canIsoPeptide',
        'piscesScore1': 'canIsoScore',
    }).select([
        'source', 'scan', 'canIsoPeptide', 'canIsoScore'
    ]).filter(
        pl.col('canIsoScore').gt(score_cut_off)
    )
    isobar_df.write_csv(f'{config.output_folder}/canonical_isobars.csv')

    nc_df = nc_df.join(isobar_df.select(
        ['source', 'scan', 'canIsoPeptide', 'canIsoScore']
    ), how='left', on=['source', 'scan'])
    nc_df = nc_df.filter(pl.col('canIsoPeptide').is_null()).drop(
        ['canIsoPeptide', 'canIsoScore']
    )

    nc_df.write_csv(f'{config.output_folder}/full_filtered_psms.csv')

    return pl.concat([can_contam_df, nc_df.drop('stratum')])
