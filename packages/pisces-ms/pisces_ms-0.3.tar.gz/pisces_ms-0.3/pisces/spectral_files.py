""" Functions for reading in scans results in mgf format.
"""
import os
import re

import polars as pl
from pyteomics import mgf
from pisces.constants import PROTON


def process_mgf_file(
        mgf_filename,
    ):
    """ Function to process an mgf file to find matches with scan IDs.

    Parameters
    ----------
    mgf_filename : str
        The mgf file from which we are reading.
    scan_ids : set of int
        A set of the scan IDs we require.
    scan_file_format : str
        The format of the file used.
    source_list : list of str
        A list of source names.

    Returns
    -------
    scans_df : pd.DataFrame
        A DataFrame of scan results.
    """
    scan_ids = []
    sources = []
    charges = []
    rts = []
    source = mgf_filename.split('/')[-1][:-4]
    mass_list = []


    with mgf.read(mgf_filename) as reader:
        for spectrum in reader:
            if 'scans' in spectrum['params']:
                scan_id = int(spectrum['params']['scans'])
            else:
                regex_match = re.match(
                    r'(\d+)(.*?)',
                    spectrum['params']['title'].split('scan=')[-1]
                )
                scan_id = int(regex_match.group(1))
            try:
                charge = int(spectrum['params']['charge'][0])
                pep_mz = float(spectrum['params']['pepmass'][0])
                rt = float(spectrum['params']['rtinseconds'])
                pep_mass = (pep_mz*charge) - (PROTON*charge)
                sources.append(source)
                scan_ids.append(scan_id)
                charges.append(charge)
                rts.append(rt)
                mass_list.append(pep_mass)
            except Exception as e:
                print(f'Failed for scan {scan_id} with Exception {e}')
                continue

    mgf_data = {
        'source': pl.Series(sources), 'scan': pl.Series(scan_ids),
        'mass': pl.Series(mass_list), 'charge': pl.Series(charges),
        'retentionTime': pl.Series(rts),
    }

    mgf_df = pl.DataFrame(mgf_data)
    mgf_df = mgf_df.unique(subset=['source', 'scan'])

    return mgf_df



def fetch_spectra(scans_folder):
    """ Function to get all MS2 spectra and from mgf files.
    """
    scan_dfs = []
    for scan_file in os.listdir(scans_folder):
        if scan_file.endswith('.mgf'):
            scan_dfs.append(process_mgf_file(f'{scans_folder}/{scan_file}'))

    return pl.concat(scan_dfs).sort(by='mass')

def retrieve_ms_details(scans_folder):
    """ Function to fetch charge, retention time, and mass of a scan.
    """
    spectra_df = fetch_spectra(scans_folder)
    return spectra_df.select(
        ['source', 'scan', 'charge', 'retentionTime', 'mass']
    )


def retrieve_charge(nc_df, scans_folder):
    """ Function to fetch charge for MS2 scans.
    """
    spectra_df = fetch_spectra(scans_folder)
    nc_df = nc_df.join(
        spectra_df[['source', 'scan', 'charge']],
        on=['source', 'scan'],
        how='inner',
    )
    return nc_df

def retrieve_rt(nc_df, scans_folder):
    """ Function to fetch charge for MS2 scans.
    """
    spectra_df = fetch_spectra(scans_folder)
    nc_df = nc_df.join(
        spectra_df[['source', 'scan', 'retentionTime']],
        on=['source', 'scan'],
        how='inner',
    )
    return nc_df
