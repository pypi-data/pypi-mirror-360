""" Suite of functions for finding expressed proteins in an enlarged database.
"""
import os
import multiprocessing as mp

import polars as pl

from pisces.constants import MASS_DIFF_CUT
from pisces.construct_junction_utils import find_junction_peptides
from pisces.construct_proteome_utils import (
    create_tags, extend_peptide, extend_peptide_tag,
    get_mw, get_relevant_proteins, write_prot_fasta,
)
from pisces.proteome_utils import distribute_mapping
from pisces.spectral_files import retrieve_ms_details
from pisces.utils import divide_df

CONTAMS_PATH = '/data/John/ALL_FINAL/contams.fasta'

def construct_proteome(config):
    """ Select PSMs that map to six frame translated genome and push target
        and decoy through inSPIRE.
    """
    psms_df, top_df, unique_pep_df = fetch_dataframes(config)
    spectral_df = retrieve_ms_details(config.scans_folder)

    psm_dfs = []
    # We search the contaminants database first, so that those
    # peptides are not included downstream.
    # We then search target and decoy for the six frame proteome.
    for db, prefix in zip(
        [CONTAMS_PATH, config.proteome, config.proteome],
        ['CONTAMS_', '', 'rev_'],
    ):
        print(f'Mapping {db} with prefix {prefix}')
        # Find direct matches to 6 frame translated proteome.
        direct_df = distribute_mapping(
            unique_pep_df, db, 'sixFrame', config.n_cores,
            with_splicing=False, max_intervening=config.max_intervening,
            prefix=prefix, filter_not_mapped=True, n_core_multiplier=4,
            tree_size=config.tree_size,
        )

        # Get the direct matches to the six frame translated proteome.
        target_df = psms_df.join(
            direct_df.rename({'sixFrame_Proteins': 'proteins'}).select(
                'peptide', 'proteins'
            ),
            how='inner', on='peptide',
        )

        # Check if peptides are mw matched to the corresponding spectrum
        # for peptides which were too small, we extend the peptide to fit the
        # mass of the spectrum.
        target_df = match_mws(
            target_df, spectral_df, db, prefix
        )

        # Next check peptides which do not match directly but have substrings
        # present in the database. We will extend these peptides to fit the
        # mass of the spectrum.
        target_df = add_fuzzy_mapped_peptides(
            config,
            target_df,
            top_df,
            spectral_df,
            db, prefix,
        )

        # Add label of target or decoy.
        if prefix.startswith('rev'):
            target_df = target_df.with_columns(pl.lit(-1).alias('Label'))
        else:
            target_df = target_df.with_columns(pl.lit(1).alias('Label'))

        psm_dfs.append(target_df)

    # Combine all the dataframes and remove duplicates.
    total_df = pl.concat(psm_dfs)
    total_df = total_df.join(
        spectral_df.select(['source', 'scan', 'charge', 'retentionTime']),
        how='inner', on=['source', 'scan']
    )
    total_df = total_df.filter(pl.col('proteins').str.len_chars().gt(0))
    total_df = total_df.sort(by=['Label', 'Score'], descending=True)
    total_df = total_df.unique(
        ['source', 'scan', 'peptide'], maintain_order=True,
    )
    total_df.write_csv(
        f'{config.output_folder}/all_remapped_psms.csv'
    )

    # Write the directly mapped proteins to a fasta file used in mapping
    # of junction peptides.
    write_prot_fasta(total_df, config, 1, '', config.proteome, 'direct_mappings_target')

    # Get all junction proteins:
    final_prot_df = find_junction_peptides(config)

    # Write the final search fasta file (junction proteins combined with target
    # and decoy proteins).
    with open(f'{config.output_folder}/final_search.fasta', 'w', encoding='UTF-8') as fasta_file:
        final_prot_df.with_columns(
            pl.struct(['proteins', 'protSeqs']).map_elements(
                lambda x : fasta_file.write(f'>{x["proteins"]}\n{x["protSeqs"]}\n'),
                return_dtype=pl.Int64,
            )
        )
    write_prot_fasta(total_df, config, -1, '', config.proteome, 'final_search', mode='a')

    # For rerunning, avoid reusing the formated_df.csv file.
    if os.path.exists(f'{config.output_folder}/filteredSearch/formated_df.csv'):
        os.system(f'rm {config.output_folder}/filteredSearch/formated_df.csv')

    # Run inSPIRE on the PISCES selected database.
    config.run_inspire('Filtered Proteome', 'fragger')
    config.run_inspire('Filtered Proteome', 'core')


def fetch_dataframes(config):
    """ Function to fetch the dataframes from the output folder.
    """
    psms_df = pl.read_csv(
        f'{config.output_folder}/all_scored_candidates.csv',
        columns=['source', 'scan', 'peptide', 'modifiedSequence', 'piscesScore1'],
    )
    top_df = pl.read_csv(
        f'{config.output_folder}/all_top_candidates.csv',
        columns=['source', 'scan', 'peptide', 'modifiedSequence',],
    )

    psms_df = psms_df.filter(pl.col('peptide').str.len_chars().ge(8))
    psms_df = psms_df.with_columns(
        pl.col('source').cast(pl.String)
    )

    psms_df = psms_df.rename({'piscesScore1': 'Score'})
    unique_pep_df = psms_df.select(['peptide']).unique()

    return psms_df, top_df, unique_pep_df


def match_mws(target_df, spectral_df, db, prefix):
    """ Function to match the mass of the peptide to the mass of the
        corresponding spectrum.

    Parameters
    ----------
    target_df : pl.DataFrame
        DataFrame containing the peptide sequences and their corresponding
        spectra.
    scans_folder : str
        Path to the folder containing the spectra files.
    db : str
        Path to the database file.
    prefix : str
        Prefix to be added to the protein names.
    """
    target_df = target_df.with_columns(
        pl.struct(['peptide', 'modifiedSequence']).map_elements(
            get_mw, return_dtype=pl.Float64,
        ).alias('peptideMW')
    )
    target_df = target_df.join(
        spectral_df.select(['source', 'scan', 'mass']),
        how='inner', on=['source', 'scan'],
    )

    # Get psms where peptides mass matches their spectrum and psms where peptide is too
    # small for the spectrum.
    match_df, small_pep_df = filter_by_mass_diff(target_df)
    match_df = match_df.drop(['mass', 'peptideMW', 'massDiff'])

    # For peptides which are too small for the spectrum, extend them to fit the mass
    # of the spectrum.
    extended_pep_df = extend_peptides_to_fit_mass(small_pep_df, db, prefix)
    extended_pep_df = extended_pep_df.select(match_df.columns)

    return pl.concat([match_df, extended_pep_df])


def filter_by_mass_diff(target_df):
    """ Function to filter PSMs based on the mass difference between the peptide
        and the mass of the corresponding spectrum.
    """
    target_df = target_df.with_columns(
        (pl.col('mass') - pl.col('peptideMW')).alias('massDiff')
    )
    target_df = target_df.filter(
        pl.col('massDiff').gt(-MASS_DIFF_CUT)
    )

    over_df = target_df.filter(
        pl.col('massDiff').gt(MASS_DIFF_CUT) &
        (pl.col('massDiff')-1).abs().gt(MASS_DIFF_CUT) &
        (pl.col('massDiff')-2).abs().gt(MASS_DIFF_CUT)
    )

    match_df = target_df.filter(
        pl.col('massDiff').abs().le(MASS_DIFF_CUT) |
        (pl.col('massDiff')-1).abs().le(MASS_DIFF_CUT) |
        (pl.col('massDiff')-1).abs().le(MASS_DIFF_CUT)
    )
    return match_df, over_df


def extend_peptides_to_fit_mass(over_df, db, prefix):
    """ Function to extend the peptides to fit the mass of the spectrum.
    """
    relevant_proteins = get_relevant_proteins(
        over_df.with_columns(pl.col('proteins').str.split(by=' ')), db, 'proteins', prefix=prefix
    )
    over_df = over_df.with_columns(
        pl.struct(['peptide', 'modifiedSequence', 'massDiff', 'proteins']).map_elements(
            lambda x : extend_peptide(
                x['peptide'], x['modifiedSequence'], x['massDiff'], x['proteins'], relevant_proteins
            ), return_dtype=pl.Struct([
                pl.Field('peptide', pl.List(pl.String)),
                pl.Field('modifiedSequence', pl.List(pl.String)),
                pl.Field('massDiff', pl.List(pl.Float64)),
                pl.Field('proteins', pl.List(pl.String)),
            ])
        ).alias('results')
    )
    over_df = over_df.drop(['peptide', 'modifiedSequence', 'massDiff', 'proteins'])
    over_df = over_df.unnest('results')
    over_df = over_df.explode(['peptide', 'modifiedSequence', 'massDiff', 'proteins'])
    over_df = over_df.drop_nulls(subset=['peptide'])

    over_df = over_df.group_by(
        ['source', 'scan', 'peptide', 'modifiedSequence',]
    ).agg(pl.col('proteins'))
    over_df = over_df.with_columns(
        pl.col('proteins').list.join(' ')
    )
    if 'Score' in over_df.columns:
        over_df = over_df.drop('Score')
    over_df = over_df.with_columns(
        pl.lit(0.0, dtype=pl.Float64).alias('Score')
    )
    return over_df

def add_fuzzy_mapped_peptides(config, mapped_df, top_ranked_df, spectral_df, db, prefix):
    """ Function to peptides that have a substring present in the database
        and construct a suitable peptide sequence for scan MW.

    Parameters
    ----------
    config : Config
        Configuration object containing the parameters for the analysis.
    top_ranked_df : pl.DataFrame
        DataFrame containing the peptide sequences and their corresponding
        spectra.
    db : str
        Path to the database file.
    prefix : str
        Prefix to be added to the protein names.
    """
    unique_unmapped_df = top_ranked_df.join(mapped_df.select(['peptide']), how='anti', on='peptide')
    unique_unmapped_df = unique_unmapped_df.select(['peptide']).unique()

    # Explode to get map 5mers.
    unique_unmapped_df = unique_unmapped_df.rename({'peptide': 'sourcePeptide'})
    unique_unmapped_df = unique_unmapped_df.with_columns(
        pl.col('sourcePeptide').map_elements(
            create_tags, return_dtype=pl.List(pl.String),
        ).alias('peptide')
    )

    unique_unmapped_df = unique_unmapped_df.explode('peptide')
    unique_unmapped_df = unique_unmapped_df.drop_nulls(subset=['peptide'])

    fuzzy_matched_df = distribute_mapping(
        unique_unmapped_df,
        db,
        'sixFrameFuzzy',
        config.n_cores,
        with_splicing=False,
        max_intervening=config.max_intervening,
        prefix=prefix,
        filter_not_mapped=True,
        n_core_multiplier=4,
        tree_size=config.tree_size,
    )

    relevant_proteins = get_relevant_proteins(
        fuzzy_matched_df.with_columns(pl.col('sixFrameFuzzy_Proteins').str.split(by=' ')),
        db, 'sixFrameFuzzy_Proteins', prefix=prefix
    )
    remapped_df = unique_unmapped_df.join(
        fuzzy_matched_df, how='left', on='peptide',
    )
    remapped_df = remapped_df.group_by(
        'sourcePeptide'
    ).agg(
        pl.col('sixFrameFuzzy_Proteins').alias('proteins'),
        pl.col('peptide').alias('tags'),
    )

    remapped_df = remapped_df.filter(
        pl.col('proteins').map_elements(
            lambda x : max([y is not None for y in x]), return_dtype=pl.Boolean,
        )
    )
    remapped_df = remapped_df.rename({'sourcePeptide': 'peptide'})
    top_ranked_df = top_ranked_df.join(remapped_df, how='inner', on='peptide')
    top_ranked_df = top_ranked_df.join(
        spectral_df.select(['source', 'scan', 'mass']),
        how='inner', on=['source', 'scan'],
    )

    divided_dfs = divide_df(top_ranked_df, config.n_cores)
    func_args = []
    for df in divided_dfs:
        func_args.append((df, relevant_proteins))

    with mp.get_context('spawn').Pool(processes=config.n_cores) as pool:
        results_dfs = pool.starmap(fuzzy_match_via_extension, func_args)
    fuzzy_df = pl.concat(results_dfs)

    fuzzy_df = fuzzy_df.group_by(
        ['source', 'scan', 'peptide', 'modifiedSequence']
    ).agg(
        pl.col('proteins')
    )
    fuzzy_df = fuzzy_df.with_columns(pl.col('proteins').list.join(' '))

    fuzzy_df = fuzzy_df.with_columns(
        pl.lit(0.0, dtype=pl.Float64).alias('Score')
    )

    return pl.concat([mapped_df, fuzzy_df.select(mapped_df.columns)])


def fuzzy_match_via_extension(top_ranked_df, relevant_proteins):
    """ Function to extend the peptides so that they match the mass of the
        corresponding spectrum.
    """
    top_ranked_df = top_ranked_df.with_columns(
        pl.struct(['peptide', 'tags', 'mass', 'proteins']).map_elements(
            lambda x : extend_peptide_tag(
                x['peptide'], x['tags'], x['mass'], x['proteins'], relevant_proteins
            ), return_dtype=pl.Struct([
                pl.Field('peptide', pl.List(pl.String)),
                pl.Field('proteins', pl.List(pl.String)),
            ])
        ).alias('results')
    )

    top_ranked_df = top_ranked_df.drop(['peptide', 'modifiedSequence', 'proteins'])
    top_ranked_df = top_ranked_df.unnest('results')
    top_ranked_df = top_ranked_df.explode(['peptide', 'proteins'])

    top_ranked_df = top_ranked_df.drop_nulls(subset=['peptide'])
    top_ranked_df = top_ranked_df.with_columns(
        pl.col('peptide').str.replace_many(
            ['C', 'm', 'n', 'q', '_'], ['C[+57.0]', 'M[+16.0]', 'N[+1.0]', 'Q[+1.0]', '[+42.0]'],
        ).alias('modifiedSequence')
    )
    top_ranked_df = top_ranked_df.with_columns(
        pl.col('peptide').str.replace_many(
            ['m', 'n', 'q', '_'], ['M', 'N', 'Q', ''],
        )
    )
    top_ranked_df = top_ranked_df.group_by(
        ['source', 'scan', 'peptide', 'modifiedSequence']
    ).agg(
        pl.col('mass').first(),
        pl.col('proteins')
    ).with_columns(
        pl.col('proteins').list.join(' ')
    )

    return top_ranked_df
