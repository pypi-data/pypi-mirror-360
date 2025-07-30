""" Functions to handle cryptic processing.
"""
import multiprocessing as mp
import regex as re

import polars as pl
from suffix_tree import Tree

from pisces.constants import (
    C_TERMINUS, EMPTY_SPLICING_RESULTS, N_TERMINUS, RESIDUE_WEIGHTS_MOD
)
from pisces.splicing_utils import remap_to_spliced_proteome, combine_accessions

SPLICED_ACCESSION_DTYPE = pl.Struct([
    pl.Field("nSplicedProteins", pl.Int64),
    pl.Field("splicedProteins", pl.String),
    pl.Field("sr1_Index", pl.String),
    pl.Field("sr2_Index", pl.String),
    pl.Field("sr1", pl.String),
    pl.Field("interveningSeqLengths", pl.String),
    pl.Field("isForward", pl.String),
])


def get_mw(peptide):
    """ Helper function to get the molecular weight of a peptide.
    """
    return sum(
        (RESIDUE_WEIGHTS_MOD[a_a] for a_a in peptide)
    ) + C_TERMINUS + N_TERMINUS


def handle_proteome_chunk(
        expanded_proteome, start_index, prots_to_process, peptide_df,
        tree_size=500, splicing=False, max_intervening=None, prefix='',
        check_preceding=None,
    ):
    """ Function to handle a chunk of the proteome.

    Parameters
    ----------
    expanded_proteome : str
        Path to a proteome file.
    start_index : int
        The index from which the peptides should be read.
    prots_to_process : int
        The number of proteins to process.
    """
    peptide_df = peptide_df.with_columns(
        pl.lit('').alias('accession')
    )
    if prots_to_process == 0 or peptide_df.shape[0] == 0:
        return peptide_df
    divisor = max([1, prots_to_process//tree_size])
    processing_splits = [
        prots_to_process//divisor
    ]*divisor
    for idx in range(prots_to_process%divisor):
        processing_splits[idx] += 1

    with open(expanded_proteome, 'r', encoding='UTF-8') as prot_file:
        line, prot_file = skip_to_prot_start(prot_file, start_index)
        for sub_prots_to_proc in processing_splits:
            suff_tree, proteome_dict, prot_file, line = build_tree(
                prot_file, sub_prots_to_proc, splicing, line, prefix, check_preceding
            )

            if splicing:
                peptide_df = peptide_df.with_columns(
                    pl.struct(['peptide', 'accession']).map_elements(
                        lambda df_row, prot=proteome_dict, st=suff_tree : remap_to_spliced_proteome(
                            df_row['peptide'],
                            df_row['accession'],
                            prot,
                            st,
                            max_intervening,
                        ),
                        return_dtype=pl.String,
                    ).alias('accession')
                )
            else:
                peptide_df = peptide_df.with_columns(
                    pl.struct(['peptide', 'accession']).map_elements(
                        lambda df_row, st=suff_tree : find_in_tree(
                            df_row['peptide'],
                            df_row['accession'],
                            st,
                            proteome_dict=proteome_dict,
                            check_preceding=check_preceding,
                        ),
                        return_dtype=pl.String
                    ).alias('accession')
                )
    return peptide_df


def build_tree(prot_file, sub_prots_to_proc, splicing, line, prefix, check_preceding=None):
    """ Function to build suffix tree from a subsection of a fasta file.
    """
    sub_prots_proc_count = 0
    suff_tree = Tree()
    proteome_dict = {}

    while (sub_prots_proc_count < sub_prots_to_proc) and line:
        prot_name = line.strip('>').split(' ')[0].strip('\n')
        if prefix:
            prot_name = prefix + prot_name
        line = prot_file.readline()
        prot = ''
        while not line.startswith('>') and line:
            if len(prot) < 100_000:
                prot += line.strip('\n')
            line = prot_file.readline()

        if len(prot) < 100_000:
            il_prot = prot.replace('I', 'L')
            if prefix.startswith('rev'):
                il_prot = il_prot[::-1]
            if splicing or check_preceding is not None:
                proteome_dict[prot_name] = il_prot
            suff_tree.add(prot_name, il_prot)
        else:
            print(f'Warning: Skipping {prot_name} due to length restriction.')
        sub_prots_proc_count += 1

    return suff_tree, proteome_dict, prot_file, line


def divide_proteome_across_cores(proteome_file, n_cores):
    """ Function to count proteins in a proteome file and divide mapping of the
        proteins up across cores.
    """
    prot_count = 0
    with open(proteome_file, 'r', encoding='UTF-8') as prot_file:
        line = prot_file.readline()
        while line:
            if line.startswith('>'):
                prot_count += 1
            line = prot_file.readline()

    n_prots_per_core = prot_count//n_cores
    extra_prot_cores = prot_count%n_cores
    prots_per_core = [
        n_prots_per_core + 1 if idx < extra_prot_cores else n_prots_per_core for idx in range(
            n_cores
        )
    ]
    start_idx_per_core = []
    start_idx = 0
    for idx in range(n_cores):
        start_idx_per_core.append(start_idx)
        start_idx += prots_per_core[idx]

    return prots_per_core, start_idx_per_core


def distribute_mapping(
        fdr_est_df, expanded_proteome, stratum_name, n_cores,
        tree_size=500, with_splicing=False, max_intervening=None,
        allow_can_mm=False, prefix='', filter_not_mapped=False,
        check_preceding=None, n_core_multiplier=1
    ):
    """ Functions to distribute mappings.
    """
    n_jobs = n_cores * n_core_multiplier
    prots_per_core, start_idx_per_core = divide_proteome_across_cores(
        expanded_proteome, n_jobs
    )

    peptides = fdr_est_df.select(['peptide']).unique()
    func_args = [
        (
            expanded_proteome,
            start_idx_per_core[idx],
            prots_per_core[idx],
            peptides,
            tree_size,
            False,
            None,
            prefix,
            check_preceding,
        ) for idx in range(n_jobs)
    ]
    with mp.get_context('spawn').Pool(processes=n_cores) as pool:
        results = pool.starmap(handle_proteome_chunk, func_args)

    for idx, accession_df in enumerate(results):
        accession_df = accession_df.rename({
            'accession': f'accession_{idx}'
        })

        if idx == 0:
            total_acc_df = accession_df
        else:
            total_acc_df = total_acc_df.join(accession_df, how='inner', on='peptide')

    protein_col_name = f'{stratum_name}_Proteins'
    protein_count_col_name = f'{stratum_name}_nProteins'

    total_acc_df = total_acc_df.with_columns(
        pl.struct([f'accession_{acc_idx}' for acc_idx in range(n_jobs)]).map_elements(
            lambda df_row : ' '.join([
                df_row[f'accession_{acc_idx}'] for acc_idx in range(
                    n_jobs
                ) if df_row[f'accession_{acc_idx}']
            ]).strip(' '),
            return_dtype=pl.String,
        ).alias(protein_col_name)
    )
    total_acc_df = total_acc_df.drop([f'accession_{acc_idx}' for acc_idx in range(n_jobs)])

    total_acc_df = total_acc_df.with_columns(
        pl.col(protein_col_name).map_elements(
            lambda x : len(set(x.strip(' ').split(' '))) if x else 0,
            return_dtype=pl.Int64,
        ).alias(protein_count_col_name)
    )
    if with_splicing:
        if allow_can_mm:
            peptides = total_acc_df.select(['peptide']).unique()
        else:
            peptides = total_acc_df.filter(
                pl.col(protein_count_col_name).eq(0)
            ).select(['peptide']).unique()

        func_args = [
            (
                expanded_proteome, start_idx_per_core[idx], prots_per_core[idx],
                peptides, tree_size, True, max_intervening, prefix, check_preceding,
            ) for idx in range(n_jobs)
        ]
        with mp.get_context('spawn').Pool(processes=n_cores) as pool:
            accessions_spliced = pool.starmap(handle_proteome_chunk, func_args)

        for idx, accession_df in enumerate(accessions_spliced):
            accession_df = accession_df.rename({'accession': f'accession_{idx}'})

            if idx == 0:
                all_spliced_accs = accession_df
            else:
                all_spliced_accs = all_spliced_accs.join(accession_df, how='inner', on='peptide')

        all_spliced_accs = all_spliced_accs.with_columns(
            pl.struct([f'accession_{idx}' for idx in range(len(accessions_spliced))]).map_elements(
                lambda df_row : combine_accessions(df_row, len(accessions_spliced)),
                return_dtype=SPLICED_ACCESSION_DTYPE,
            ).alias('splicedResults')
        )
        all_spliced_accs = all_spliced_accs.drop(
            [f'accession_{acc_idx}' for acc_idx in range(n_jobs)]
        )

        total_acc_df = total_acc_df.join(all_spliced_accs, how='left', on='peptide')
        total_acc_df = total_acc_df.with_columns(
            pl.col('splicedResults').fill_null(
                pl.Series([EMPTY_SPLICING_RESULTS])
            )
        )

    if filter_not_mapped:
        total_acc_df = total_acc_df.filter(pl.col(protein_count_col_name).gt(0))

    return total_acc_df


def find_in_tree(peptide, accessions, suff_tree, proteome_dict=None, check_preceding=None):
    """ Function to find all peptide accessions.
    """
    pep_accessions = suff_tree.find_all(peptide)
    for acc in pep_accessions:
        if check_preceding is not None:
            prot_seq = proteome_dict[acc[0]]
            for loc in re.finditer(peptide, prot_seq):
                start_pos = loc.start()
                if start_pos == 0 or prot_seq[start_pos-1] in check_preceding:
                    accessions += f'{acc[0]} '
        else:
            accessions += f'{acc[0]} '
    return accessions


def skip_to_prot_start(prot_file, start_index):
    """ Function to skip to a protein index.
    """
    line = prot_file.readline()
    prot_count = 0
    while prot_count < start_index + 1:
        if line.startswith('>'):
            prot_count += 1
            if prot_count == start_index + 1:
                break
        line = prot_file.readline()
    return line, prot_file
