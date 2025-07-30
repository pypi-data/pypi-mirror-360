""" Functions for formatting exhaustive outputs.
"""
from copy import deepcopy
from functools import reduce
import multiprocessing as mp
import operator
import os

import pandas as pd
import polars as pl

from pisces.constants import C_TERMINUS, N_TERMINUS, RESIDUE_WEIGHTS, PEPTIDE_KEY, MOD_SEQ_KEY
from pisces.inspire import run_exhaustive_inspire, BATCH_SIZE
from pisces.spectral_files import fetch_spectra


def process_spisnake_candidates(config):
    """ Function to process SPIsnake peptides.
    """
    if config.exhaustive_results is not None:
        for idx, results_dict in enumerate(config.exhaustive_results):
            get_psms(results_dict['resultsDir'], results_dict['mods'], config)
            run_exhaustive_inspire(config, idx)

def match_scans(pep_mass, filtered_scan_df):
    """ Match all MS2 spectra to a given peptide.
    """
    throw_away_idx = -1

    matches = []

    for scan_idx, scan_row in filtered_scan_df.iterrows():
        if scan_row['maxMatch'] < pep_mass:
            throw_away_idx = scan_idx
        elif scan_row['minMatch'] > pep_mass:
            break
        else:
            matches.append(scan_row['scanID'])

    if throw_away_idx > -1:
        throw_away_range = range(filtered_scan_df.index[0], throw_away_idx)
        filtered_scan_df.drop(throw_away_range, inplace=True)

    return matches

def get_mass(peptide, mods):
    """ Get the mass the modified peptide.
    """
    residue_weights = RESIDUE_WEIGHTS.copy()
    if 'ox' in mods:
        residue_weights['M'] += 15.994915
    if 'cam' in mods:
        residue_weights['C'] += 57.021464

    return sum((residue_weights[amino_acid] for amino_acid in peptide)) + C_TERMINUS + N_TERMINUS

def create_mod_seq(peptide, mods):
    """ Function to create a modified sequence for a peptide.
    """
    if not mods:
        return peptide
    mod_seq = ''
    for a_a in peptide:
        if a_a == 'C' and 'cam' in mods:
            mod_seq += 'C[+57.0]'
        elif a_a == 'M' and 'ox' in mods:
            mod_seq += 'M[+16.0]'
        else:
            mod_seq += a_a
    return mod_seq


def process_parquet_file(
        parquet_file, scan_df, scan_files, mods,
        file_idx, output_folder, ppm_error, alleles
    ):
    """ Read in a parquet file, filter the peptides, get how many peptides match based on m/z.
    """
    # rt_filtered_cols = [f'MW.RT.exists:{scan_file}' for scan_file in scan_files]
    ic50_filtered_cols = [
        f'Predicted_binder:{scan_file}:{allele}' for scan_file in scan_files
        for allele in alleles
    ]
    spisnake_df = pd.read_parquet(parquet_file, columns=[PEPTIDE_KEY]+ic50_filtered_cols)

    spisnake_df = spisnake_df[
        (reduce(
            operator.or_,
            [spisnake_df[col] for col in ic50_filtered_cols],
        ))
    ]
    if not spisnake_df.shape[0]:
        return

    spisnake_df = spisnake_df[[PEPTIDE_KEY]]
    spisnake_df[PEPTIDE_KEY] = spisnake_df[PEPTIDE_KEY].str.replace('I', 'L')
    spisnake_df = spisnake_df.drop_duplicates(subset=[PEPTIDE_KEY])
    spisnake_df['mass'] = spisnake_df[PEPTIDE_KEY].apply(
        lambda x : get_mass(x, mods)
    )
    spisnake_df = spisnake_df.sort_values(by='mass').reset_index(drop=True)
    spisnake_min = spisnake_df['mass'].min()
    spisnake_max = spisnake_df['mass'].max()

    max_error = (
        spisnake_df['mass'].iloc[spisnake_df.shape[0]-1] * ppm_error
    )/1_000_000

    scan_df['minMatch'] = scan_df['mass'] - max_error
    scan_df['maxMatch'] = scan_df['mass'] + max_error

    filtered_scan_df = scan_df[
        (scan_df['maxMatch'] >= spisnake_min) &
        (scan_df['minMatch'] <= spisnake_max)
    ].reset_index(drop=True)


    filtered_scan_df = filtered_scan_df[['scanID', 'minMatch', 'maxMatch']]
    spisnake_df['matchedScans'] = spisnake_df['mass'].apply(
        lambda pep_mass : match_scans(pep_mass, filtered_scan_df)
    )

    spisnake_df = spisnake_df.explode('matchedScans')

    spisnake_df = spisnake_df[
        (spisnake_df['matchedScans'].notna()) &
        (spisnake_df['matchedScans'].notnull())
    ]

    spisnake_df['scan'] = spisnake_df['matchedScans'].apply(
        lambda x : int(x.split(':')[1])
    )
    spisnake_df['source'] = spisnake_df['matchedScans'].apply(
        lambda x : scan_files[int(x.split(':')[0])]
    )

    spisnake_df[MOD_SEQ_KEY] = spisnake_df[PEPTIDE_KEY].apply(
        lambda x : create_mod_seq(x, mods)
    )

    spisnake_df[['source', 'scan', PEPTIDE_KEY, MOD_SEQ_KEY]].to_parquet(
        f'{output_folder}/holdingFolder/candidate_psms/proc_{file_idx}.parquet', index=False,
    )



def create_ptm_seq(peptide, mods):
    """ Function to create an inSPIRE ptm sequence.
    """
    ptm_seq = '0.'
    for a_a in peptide:
        if a_a == 'C' and 'cam' in mods:
            ptm_seq += '1'
        elif a_a == 'M' and 'ox' in mods:
            ptm_seq += '2'
        else:
            ptm_seq += '0'
    return ptm_seq + '.0'


def fetch_files(results_dir):
    """ Function to fetch all SPIsnake parquet files.
    """
    all_files = []
    for path, _, files in os.walk(f'{results_dir}/DB_out/arrow'):
        for name in files:
            if name.endswith('.parquet'):
                all_files.append(os.path.join(path, name))
    return all_files

def get_psms(spisnake_results_dir, mods, config):
    """ Function to create PSMs out of SPIsnake peptides.
    """
    all_files = fetch_files(spisnake_results_dir)

    spectra_df = fetch_spectra(config.scans_folder)
    spectra_df = spectra_df.to_pandas()

    assigned_can_df = pd.read_csv(f'{config.output_folder}/canonicalOutput/finalPsmAssignments.csv')
    assigned_can_df['source'] = assigned_can_df['source'].astype(str)
    assigned_can_df = assigned_can_df[assigned_can_df['postErrProb'] < 0.01]
    spectra_df = pd.merge(
        spectra_df, assigned_can_df[['source', 'scan']].drop_duplicates(),
        how='left', on=['source', 'scan'], indicator=True,
    )
    spectra_df = spectra_df[spectra_df['_merge'] == 'left_only']

    scan_files = sorted(spectra_df['source'].unique().tolist())
    spectra_df['scanID'] = spectra_df.apply(
        lambda df_row : f'{scan_files.index(df_row["source"])}:{df_row["scan"]}', axis=1,
    )
    mass_spectra_df = spectra_df[['scanID', 'mass']]

    func_args = [
        (
            pq_file, deepcopy(mass_spectra_df), scan_files, mods, file_idx,
            config.output_folder, config.ms1_accuracy, config.alleles
        ) for file_idx, pq_file in enumerate(all_files)
    ]

    with mp.get_context('spawn').Pool(processes=config.n_cores) as pool:
        pool.starmap(process_parquet_file, func_args)
    len(all_files)


    combined_df = None
    cand_psms_folder = f'{config.output_folder}/holdingFolder/candidate_psms'
    comb_count = 0
    spectra_df_pl = pl.from_pandas(spectra_df[['source', 'scan', 'charge', 'retentionTime']])
    proc_files = [in_file for in_file in os.listdir(cand_psms_folder) if in_file.startswith('proc')]
    for file in proc_files:
        psm_df = pl.read_parquet(f'{cand_psms_folder}/{file}')
        psm_df = psm_df.join(spectra_df_pl, how='inner', on=['source', 'scan'])

        if combined_df is not None:
            combined_df = pl.concat([combined_df, psm_df])
        else:
            combined_df = psm_df

        if combined_df.shape[0] > BATCH_SIZE:
            combined_df.write_csv(f'{cand_psms_folder}/combined_{comb_count}.csv')
            comb_count += 1
            combined_df = None

        os.system(
            f'rm {cand_psms_folder}/{file}'
        )

    if combined_df is not None:
        combined_df.write_csv(f'{cand_psms_folder}/combined_{comb_count}.csv')
