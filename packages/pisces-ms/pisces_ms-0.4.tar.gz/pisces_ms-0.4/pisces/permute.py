""" Functions to permute sequences.
"""
from copy import deepcopy
import os
import subprocess

import pandas as pd
import polars as pl
from pisces.constants import (
    INSPIRE_PROCESSING_PIPELINES, MOD_SEQ_KEY, PEPTIDE_KEY, SOURCE_KEY, SCAN_KEY,
)
from pisces.inspire import BATCH_SIZE, wait_on_slurm_jobs, write_slurm_scipt
from pisces.isobars import ISOBARIC_DOUBLETS, ISOBARIC_SINGLES
from pisces.preprocess import apply_post_processing
from pisces.spectral_files import retrieve_charge
from pisces.utils import modify_columns

ISOBAR_COLUMNS = [
    ['isobarCompetitor', 'isobarScore', 'isobarModSeq', 'isobarSource'],
    ['iso2peptide', 'iso2score'],
    ['iso3peptide', 'iso3score'],
]
PSM_ID_KEYS = [SOURCE_KEY, SCAN_KEY, PEPTIDE_KEY]
SCAN_ID_KEYS = [SOURCE_KEY, SCAN_KEY]

def create_doublets(config):
    """ Function to permute top ranking sequences.
    """
    all_dfs = []

    if config.enzyme == 'trypsin' or config.de_novo_method == 'casanovo':
        n_mut_rounds = 1
        mutate = False
    else:
        n_mut_rounds = 3
        mutate = True
    mutated_df = None
    for mut_idx in range(n_mut_rounds):
        unmutated_df, mutated_df = run_mutation_round(
            config,
            mutated_df,
            mutate
        )
        if mut_idx > 0:
            unmutated_df = modify_columns(
                unmutated_df, required_schema, cols
            )
        else:
            cols = unmutated_df.columns
            required_schema = unmutated_df.schema

        if unmutated_df.shape[0]:
            all_dfs.append(unmutated_df)

        config.remove_pisces_path('isobarOutput/mhcpan')
        config.remove_pisces_path('isobarOutput/formated_df.csv')
        config.remove_pisces_path('isobarOutput/formated_mods.csv')

    mutated_df = modify_columns(mutated_df, required_schema, cols)
    if mutated_df.shape[0]:
        all_dfs += [mutated_df]
    all_dfs = [df.select(cols) for df in all_dfs]

    top_candidate_df = pl.concat(all_dfs)
    top_candidate_df = top_candidate_df.sort(
        by=['piscesScore1', 'scan', 'modifiedSequence'], descending=[True, False, False],
    )
    top_candidate_df.write_csv(
        f'{config.output_folder}/double_top_candidates.csv'
    )


def run_mutation_round(config, top_candidate_df, mutate):
    """ Function to run a round of mutation.
    """
    first_mut = top_candidate_df is None
    has_exhausitve = config.exhaustive_results is not None

    if first_mut:
        top_candidate_df = pl.read_csv(f'{config.output_folder}/all_top_candidates.csv',)
        top_candidate_df = top_candidate_df.with_columns(
            pl.lit('deNovo').alias('candidateSource'),
            pl.col('source').cast(pl.String),
        )
        df_to_mutate = top_candidate_df.select(PSM_ID_KEYS + [MOD_SEQ_KEY, 'candidateSource'])
    else:
        df_to_mutate = top_candidate_df.select(
            PSM_ID_KEYS + [MOD_SEQ_KEY],
        )

    df_to_mutate = retrieve_charge(df_to_mutate, config.scans_folder)

    permut_df = permute_top_candidates(df_to_mutate, config.output_folder)
    n_jobs = permut_df.shape[0] // BATCH_SIZE
    if permut_df.shape[0] % BATCH_SIZE:
        n_jobs += 1

    permut_df = permut_df.sort(
        by=['source', 'peptide', 'modifiedSequence', 'scan'],
        descending=[False, False, False, False],
    )
    permut_dfs = permut_df.with_row_count('id').with_columns(
        pl.col('id').map_elements(
        lambda i: int(i//BATCH_SIZE),
        return_dtype=pl.Int64,
    )).partition_by('id')

    for idx, permut_df in enumerate(permut_dfs):
        permut_df.write_csv(f'{config.output_folder}/holdingFolder/isobarPsms{idx}.csv')


    if config.slurm_script is not None:
        job_ids = []
        write_slurm_scipt(config)
        for idx in range(n_jobs):
            result = subprocess.run(
                ['sbatch', 'slurm_script.sh', f'isobar_{idx}'],
                stdout=subprocess.PIPE,
                check=False,
            )
            job_ids.append(
                result.stdout.decode('utf-8').split('Submitted batch job ')[-1].strip()
            )
        wait_on_slurm_jobs(job_ids)
    else:
        for idx in range(n_jobs):
            config.move_pisces_file(
                f'holdingFolder/isobarPsms{idx}.csv',
                'holdingFolder/isobarPsms.csv',
            )
            for pipeline in INSPIRE_PROCESSING_PIPELINES:
                config.run_inspire('Isobar', pipeline)
            config.move_pisces_file(
                'isobarOutput/final_input.tab',
                f'holdingFolder/isobarPsms_processed_{idx}.tab',
            )

            config.remove_pisces_path('isobarOutput/mhcpan')
            config.remove_pisces_path('isobarOutput/formated_df.csv')

    all_isobars_df, all_original_scored_df = procress_isobar_output(
        top_candidate_df, config.output_folder, n_jobs, first_mut, has_exhausitve
    )

    isobar_dfs = get_top_iso_candidates(all_isobars_df)
    top_candidate_df = merge_isobars(
        top_candidate_df.to_pandas(),
        all_original_scored_df,
        isobar_dfs,
    )

    if first_mut:
        top_candidate_df['originalPeptide'] = deepcopy(top_candidate_df[PEPTIDE_KEY])

    top_candidate_df = top_candidate_df.apply(
        lambda df_row : switch_scores(df_row, mutate), axis=1
    )

    top_candidate_df = pl.from_pandas(top_candidate_df)
    unmutated_df = top_candidate_df.filter(
        pl.col('mutated') == 0
    )
    mutated_df = top_candidate_df.filter(
        pl.col('mutated') == 1
    )

    return unmutated_df, mutated_df


def permute_top_candidates(formated_top_c_df, output_folder):
    """ Function to permute all the top peptide candidates.
    """
    all_top_candidates = formated_top_c_df.select(
        PSM_ID_KEYS + [MOD_SEQ_KEY, 'charge']
    )
    formated_top_c_df = formated_top_c_df.with_columns(
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

    formated_top_c_df = formated_top_c_df.with_columns(
        pl.col('seqToPermute').map_elements(
            permute_peptide, skip_nulls=False, return_dtype=pl.List(pl.String),
        ).alias('substitutePep'),
    )
    formated_permut_df = formated_top_c_df.explode('substitutePep')

    formated_permut_df = formated_permut_df.with_columns(
        pl.col('substitutePep').str.replace_many(
            ['m', 'c', 'n', 'q', '_', '+', '-', '=', 'y'],
            ['M', 'C', 'N', 'Q', '', '', '', '', 'C'],
        ).alias(PEPTIDE_KEY),
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

    formated_permut_df = filter_already_scored_candidates(formated_permut_df, output_folder)

    return pl.concat([formated_permut_df.select(
        PSM_ID_KEYS + [MOD_SEQ_KEY, 'charge']
    ), all_top_candidates])


def permute_peptide(peptide):
    """ Function to permute peptide sequence to get isobar competitors.
    """
    acetylated = False
    carbamylated = False
    nh3_loss = False
    combo_mod = False
    if peptide.startswith('_'):
        peptide = peptide[1:]
        acetylated = True
    elif peptide.startswith('+'):
        peptide = peptide[1:]
        carbamylated = True
    elif peptide.startswith('-'):
        peptide = peptide[1:]
        nh3_loss = True
    elif peptide.startswith('='):
        peptide = peptide[1:]
        combo_mod = True

    swap_peps = set()

    for pos_idx, a_a in enumerate(peptide):
        isobars = ISOBARIC_SINGLES.get(a_a, [])
        for isobar in isobars:
            swap_peps.add(peptide[:pos_idx] + isobar + peptide[pos_idx+1:])

    for pos_idx in range(0, len(peptide)-1):
        doublet = peptide[pos_idx: pos_idx+2]
        isobars = ISOBARIC_DOUBLETS.get(doublet, [])
        for isobar in isobars:
            swap_peps.add(peptide[:pos_idx] + isobar + peptide[pos_idx+2:])

    for pos_idx in range(0, len(peptide)-2):
        triplet = peptide[pos_idx: pos_idx+3]
        for mod_triplet in (
            triplet[::-1],
            triplet[2] + triplet[0] + triplet[1],
            triplet[1] + triplet[2] + triplet[0],
        ):
            swap_peps.add(peptide[:pos_idx] + mod_triplet + peptide[pos_idx+3:])

    if acetylated:
        swap_peps = {'_'+x for x in swap_peps}
        if peptide[0] == 'S':
            swap_peps.add('E' + peptide[1:])
    elif carbamylated:
        swap_peps = {'+'+x for x in swap_peps}
    elif nh3_loss:
        swap_peps = {'-'+x for x in swap_peps}
    elif combo_mod:
        swap_peps = {'='+x for x in swap_peps}
    else:
        if peptide[0] == 'E':
            swap_peps.add('_S'+peptide[1:])

    return list(swap_peps)


def filter_already_scored_candidates(permuted_df, output_folder):
    """ Function to remove candidates already suggested by PEAKS de novo.
    """
    # Flag isobars which were already scored as de novo candidates.
    all_scored_candidates = pl.read_csv(
        f'{output_folder}/all_scored_candidates.csv', columns=PSM_ID_KEYS
    )
    all_scored_candidates = all_scored_candidates.with_columns(
        pl.lit('yes').alias('alreadyScored'),
        pl.col('source').cast(pl.String),
    )
    permuted_df = permuted_df.join(
        all_scored_candidates,
        on=PSM_ID_KEYS,
        how='left',
    )
    permuted_df = permuted_df.with_columns(
        pl.col('alreadyScored').fill_null('no')
    )
    permuted_df = permuted_df.filter(
        pl.col('alreadyScored').eq('no')
    )
    return permuted_df


def procress_isobar_output(top_candidate_df, output_folder, n_jobs, first_mut, has_exhausitve):
    """ Function to process the outputs of isobar inSPIRE.
    """
    all_isobars_df = pl.concat([
        pl.read_csv(
            f'{output_folder}/holdingFolder/isobarPsms_processed_{idx}.tab', separator='\t'
        ) for idx in range(n_jobs)
    ])
    all_isobars_df = all_isobars_df.with_columns(
        pl.lit('mutation').alias('isobarSource')
    )

    if first_mut and has_exhausitve:
        exhaustive_dfs = []
        for exh_file in os.listdir(f'{output_folder}/holdingFolder/candidate_psms'):
            if exh_file.startswith('final'):
                exh_df = pl.read_csv(
                    f'{output_folder}/holdingFolder/candidate_psms/{exh_file}', separator='\t'
                )
                exh_df = exh_df.filter(
                    pl.col('piscesScore1').gt(0.01)
                )
                exhaustive_dfs.append(exh_df)
        all_exhaustive_df = pl.concat(exhaustive_dfs)

        all_exhaustive_df = all_exhaustive_df.with_columns(
            pl.lit('exhaustive').alias('isobarSource')
        )
        all_isobars_df = pl.concat([all_isobars_df, all_exhaustive_df])


    all_isobars_df = all_isobars_df.unique('specID', maintain_order=True)
    all_isobars_df = apply_post_processing(all_isobars_df)
    all_isobars_df = all_isobars_df.with_columns(
        pl.col('source').cast(pl.String)
    )

    all_isobars_df = all_isobars_df.rename({
        'piscesScore1': 'secondScore',
    })

    top_candidate_df = top_candidate_df.with_columns(pl.lit('yes').alias('original'))
    all_isobars_df = all_isobars_df.join(
        top_candidate_df[PSM_ID_KEYS + ['original']],
        how='left',
        on=PSM_ID_KEYS,
    )
    all_isobars_df = all_isobars_df.with_columns(
        pl.col('original').fill_null('no')
    )

    all_original_scored_df = all_isobars_df.filter(pl.col('original') == 'yes').drop('original')
    all_true_isobars_df = all_isobars_df.filter(pl.col('original') != 'yes').drop('original')
    all_true_isobars_df = all_true_isobars_df.sort(
        by=['secondScore', SCAN_KEY, MOD_SEQ_KEY], descending=[True, False, False],
    )
    all_original_scored_df = all_original_scored_df.sort(
        by=['secondScore', SCAN_KEY, MOD_SEQ_KEY], descending=[True, False, False],
    )

    return all_true_isobars_df.to_pandas(), all_original_scored_df.to_pandas()


def get_top_iso_candidates(all_isobars_df):
    """ Function to return three Dataframes of the best isobar competitors.
    """
    all_isobars_df['isoRank'] = all_isobars_df.groupby(
        SCAN_ID_KEYS
    )['secondScore'].transform(
        'rank', method='first', ascending=False,
    )
    top_isobars_df = all_isobars_df[all_isobars_df['isoRank'] == 1].rename(
        columns={
            'secondScore': 'isobarScore',
            PEPTIDE_KEY: 'isobarCompetitor',
            MOD_SEQ_KEY: 'isobarModSeq',
        }
    )
    second_iso_df = all_isobars_df[all_isobars_df['isoRank'] == 2].rename(
        columns={
            'secondScore': 'iso2score',
            PEPTIDE_KEY: 'iso2peptide',
        }
    )
    third_iso_df = all_isobars_df[all_isobars_df['isoRank'] == 3].rename(
        columns={
            'secondScore': 'iso3score',
            PEPTIDE_KEY: 'iso3peptide',
        }
    )

    return [top_isobars_df, second_iso_df, third_iso_df]


def merge_isobars(
        top_candidate_df, all_original_scored_df, iso_dfs,
    ):
    """ Function to merge in isobars.
    """
    if 'secondScore' not in top_candidate_df.columns:
        top_candidate_df = pd.merge(
            top_candidate_df,
            all_original_scored_df[
                PSM_ID_KEYS + ['secondScore']
            ].drop_duplicates(subset=PSM_ID_KEYS),
            how='inner',
            on=PSM_ID_KEYS,
        )

    for iso_idx, iso_df in enumerate(iso_dfs):
        for iso_col in ISOBAR_COLUMNS[iso_idx]:
            if iso_col in top_candidate_df.columns:
                top_candidate_df = top_candidate_df.drop(iso_col, axis=1)

        top_candidate_df = pd.merge(
            top_candidate_df,
            iso_df[SCAN_ID_KEYS + ISOBAR_COLUMNS[iso_idx]],
            how='left',
            on=SCAN_ID_KEYS,
        )

    for iso_col in ('isobarScore', 'iso2score', 'iso3score'):
        top_candidate_df[iso_col] = top_candidate_df[iso_col].fillna(0)

    return top_candidate_df


def switch_scores(df_row, mutate=True):
    """ Function to switch peptides.
    """
    if (
        not mutate or (
            df_row['secondScore'] >= df_row['isobarScore'] or
            df_row['piscesScore1'] >= df_row['isobarScore']
        )
    ):
        df_row['isoDeltaScore'] = df_row['secondScore'] - df_row['isobarScore']
        df_row['isoDelta2Score'] = df_row['secondScore'] - df_row['iso2score']
        df_row['isoDelta3Score'] = df_row['secondScore'] - df_row['iso3score']
        df_row['mutated'] = 0
        return df_row

    peptide = df_row['isobarCompetitor']
    iso_peptide = df_row[PEPTIDE_KEY]
    mod_seq = df_row['isobarModSeq']
    iso_mod_seq = df_row[MOD_SEQ_KEY]
    score_diff = df_row['isobarScore'] - df_row['piscesScore1']

    df_row['piscesScore1'] += score_diff
    df_row[MOD_SEQ_KEY] = mod_seq
    df_row['isobarModSeq'] = iso_mod_seq
    df_row[PEPTIDE_KEY] = peptide
    df_row['isobarCompetitor'] = iso_peptide
    df_row['candidateSource'] = df_row['isobarSource']

    comp_scores = sorted([df_row['secondScore'], df_row['iso2score'], df_row['iso3score']])

    df_row['isoDeltaScore'] = df_row['isobarScore'] - comp_scores[2]
    df_row['isoDelta2Score'] = df_row['isobarScore'] - comp_scores[1]
    df_row['isoDelta3Score'] = df_row['isobarScore'] - comp_scores[0]

    df_row['secondScore'] = df_row['isobarScore']
    df_row['deltaScore'] += score_diff
    df_row['delta3Score'] += score_diff
    df_row['mutated'] = 1

    return df_row
