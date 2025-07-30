""" Utility functions for constructing an unanotated proteome.
"""
import re

import polars as pl

from pisces.constants import (
    C_TERMINUS, DEAMIDATION_DICT, MASS_DIFF_CUT, N_TERMINUS, MOD_WEIGHTS,
    RESIDUE_WEIGHTS_MOD, TAG_LENGTH, RESIDUE_WEIGHTS
)


def get_mw(df_row):
    """ Function to calculate the molecular weight of a peptide.
    """
    weight = sum(
        (RESIDUE_WEIGHTS[a_a] for a_a in df_row['peptide'])
    ) + C_TERMINUS + N_TERMINUS
    for mod, mod_wt in MOD_WEIGHTS.items():
        mod_count = df_row['modifiedSequence'].count(mod)
        weight += mod_count * mod_wt
    return weight


def _check_mass_diff(mass_diff, cut_off=MASS_DIFF_CUT, base_mass=None):
    """ Function to check if the mass difference is within the cut-off.
    """
    if base_mass is not None:
        cut_off = 10*base_mass/1_000_000

    return (
        abs(mass_diff) <= cut_off
    ) or (
        abs(mass_diff - 1) <= cut_off
    ) or (
        abs(mass_diff - 2) <= cut_off
    )


def fetch_deam_tags(peptide):
    """ Function to fetch deamidation tags for a peptide.
    """
    tags = []
    if 'D' in peptide or 'E' in peptide:
        for idx in re.finditer('D|E', peptide):
            match_pos = idx.start()
            tags.append(
                peptide[:match_pos] + DEAMIDATION_DICT[peptide[match_pos]] + peptide[match_pos+1:]
            )
    return tags


def create_tags(peptide):
    """ Function to create tags of length ~6 present in a peptide
        which could be mapped to the 6 frame translated proteome.
    """
    if len(peptide) < 8:
        return []
    if len(peptide) < 10:
        return fetch_deam_tags(peptide)
    tag_length = 6
    if len(peptide) > 20:
        mid_point_1 = len(peptide)//3-(tag_length//2)
        mid_point_2 = 2*len(peptide)//3-(tag_length//2)
        return [
            peptide[:tag_length],
            peptide[-tag_length:],
            peptide[mid_point_1:mid_point_1+tag_length],
            peptide[mid_point_2:mid_point_2+tag_length],
        ]
    mid_point = len(peptide)//2-(tag_length//2)
    return [
        peptide[:tag_length],
        peptide[-tag_length:],
        peptide[mid_point:mid_point+tag_length],
    ]


def extend_peptide_tag(
    whole_peptide, peptide_tags, scan_mw, prot_list, rel_proteins
):
    """ Function to extend peptide tags to a peptide that matches
        the molecular weight of the scan.
    """
    results = []

    for (pep_tag, prots) in zip(peptide_tags, prot_list):
        if prots is None:
            continue

        if len(pep_tag) == len(whole_peptide):
            pos = [i for i in range(len(pep_tag)) if pep_tag[i] != whole_peptide[i]][0]
            results = {
                'peptide': [pep_tag[:pos] + pep_tag[pos].lower() + pep_tag[pos+1:]],
                'proteins': [prots],
            }
            return results

        prots = [x for x in prots.split(' ') if x]
        tag_weight = sum(
            (RESIDUE_WEIGHTS_MOD[a_a] for a_a in pep_tag)
        ) + C_TERMINUS + N_TERMINUS


        for prot_id in prots:
            prot_seq = rel_proteins[prot_id].replace('I', 'L')

            prot_index = prot_seq.index(pep_tag)
            orig_mass_diff = scan_mw - tag_weight

            mass_diff_dict = {pep_tag: orig_mass_diff}
            if pep_tag.count('M') == 1:
                mass_diff_dict[pep_tag.replace('M', 'm')] = orig_mass_diff - MOD_WEIGHTS['+16.0']
            if pep_tag.count('Q') == 1:
                mass_diff_dict[pep_tag.replace('Q', 'q')] = orig_mass_diff - MOD_WEIGHTS['+1.0']
            if pep_tag.count('N') == 1:
                mass_diff_dict[pep_tag.replace('N', 'n')] = orig_mass_diff - MOD_WEIGHTS['+1.0']
            if pep_tag == whole_peptide[:TAG_LENGTH]:
                mass_diff_dict['_' + pep_tag] = orig_mass_diff - MOD_WEIGHTS['+42.0']

            for prot_index in [
                m.start() for m in re.finditer(pep_tag, prot_seq)
            ]:
                if pep_tag == whole_peptide[-TAG_LENGTH:]:
                    for idx in range(prot_index-1, -1, -1):
                        new_mass_diff_dict = create_new_mass_dict(
                            mass_diff_dict, prot_seq[idx], prepend=True
                        )
                        mass_diff_dict, results = update_mass_diff_dict(
                            results, mass_diff_dict, new_mass_diff_dict, prot_id
                        )
                        if not mass_diff_dict:
                            break
                elif pep_tag == whole_peptide[:TAG_LENGTH]:
                    for idx in range(prot_index+len(pep_tag), len(prot_seq)):
                        new_mass_diff_dict = create_new_mass_dict(
                            mass_diff_dict, prot_seq[idx], prepend=False
                        )
                        mass_diff_dict, results = update_mass_diff_dict(
                            results, mass_diff_dict, new_mass_diff_dict, prot_id
                        )
                        if not mass_diff_dict:
                            break
                else:
                    waiting_dict = {}
                    for idx in range(prot_index+len(pep_tag), len(prot_seq)):
                        new_mass_diff_dict = create_new_mass_dict(
                            mass_diff_dict, prot_seq[idx], prepend=False,
                        )
                        mass_diff_dict, results, waiting_dict = update_mass_diff_dict(
                            results, mass_diff_dict, new_mass_diff_dict,
                            prot_id, waiting_dict=waiting_dict,
                        )
                        mass_diff_dict = {}
                        for updated_peptide2, mass_diff2 in new_mass_diff_dict.items():
                            if _check_mass_diff(mass_diff2):
                                results.append((updated_peptide2, prot_id))
                                break
                            if mass_diff2 > MASS_DIFF_CUT:
                                if updated_peptide2[-1] in 'KR':
                                    waiting_dict[updated_peptide2] = mass_diff2
                                mass_diff_dict[updated_peptide2] = mass_diff2

                        if not mass_diff_dict:
                            break

                    mass_diff_dict.update(waiting_dict)
                    mass_diff_dict[pep_tag] = orig_mass_diff

                    for idx in range(prot_index-1, -1, -1):
                        new_mass_diff_dict = create_new_mass_dict(
                            mass_diff_dict, prot_seq[idx], prepend=True,
                        )

                        mass_diff_dict = {}
                        for updated_peptide2, mass_diff2 in new_mass_diff_dict.items():
                            if _check_mass_diff(mass_diff2):
                                results.append((updated_peptide2, prot_id))
                                break
                            if mass_diff2 > MASS_DIFF_CUT:
                                mass_diff_dict[updated_peptide2] = mass_diff2

                        if not mass_diff_dict:
                            break

    return {
        'peptide': [x[0] for x in results],
        'proteins': [x[1] for x in results],
    }


def extend_peptide(peptide, modified_seq, mass_diff, prots, rel_proteins):
    """ Function to extend a peptide which has a mass difference to
        the appropriate mass for the scan.
    """
    prots = [x for x in prots.split(' ') if x]
    results = []

    for prot_id in prots:
        per_prot_mass_diff = mass_diff
        prot_seq = rel_proteins[prot_id].replace('I', 'L')
        prot_index = prot_seq.index(peptide)
        if prot_index > 0 and prot_seq[prot_index-1] not in 'KR':
            continue
        updated_peptide = peptide
        updated_modified_seq = modified_seq
        for idx in range(prot_index+len(peptide), len(prot_seq)):
            updated_peptide += prot_seq[idx]
            updated_modified_seq += prot_seq[idx]
            per_prot_mass_diff -= RESIDUE_WEIGHTS_MOD[prot_seq[idx]]
            if _check_mass_diff(per_prot_mass_diff):
                results.append((per_prot_mass_diff, updated_peptide, updated_modified_seq, prot_id))
                break
            if per_prot_mass_diff < 0:
                break

    for prot_id in prots:
        per_prot_mass_diff = mass_diff
        prot_seq = rel_proteins[prot_id].replace('I', 'L')
        prot_index = prot_seq.index(peptide)
        updated_peptide = peptide
        updated_modified_seq = modified_seq
        for idx in range(prot_index-1, -1, -1):
            updated_peptide = prot_seq[idx] + updated_peptide
            updated_modified_seq = prot_seq[idx] + updated_modified_seq
            per_prot_mass_diff -= RESIDUE_WEIGHTS_MOD[prot_seq[idx]]
            if _check_mass_diff(per_prot_mass_diff):
                if idx == 0 or prot_seq[idx-1] in 'KR':
                    results.append(
                        (per_prot_mass_diff, updated_peptide, updated_modified_seq, prot_id)
                    )
                break
            if per_prot_mass_diff < 0:
                break


    return {
        'peptide': [x[1] for x in results],
        'modifiedSequence': [x[2] for x in results],
        'massDiff': [x[0] for x in results],
        'proteins': [x[3] for x in results],
    }


def update_mass_diff_dict(
    results, mass_diff_dict, new_mass_diff_dict, prot_id, waiting_dict=None
):
    """ Function to update the mass difference dictionary with new
        mass differences from peptide tags extended in different ways.
    """
    mass_diff_dict = {}
    for updated_peptide2, mass_diff2 in new_mass_diff_dict.items():
        if _check_mass_diff(mass_diff2):
            results.append((updated_peptide2, prot_id))
        elif mass_diff2 > MASS_DIFF_CUT:
            mass_diff_dict[updated_peptide2] = mass_diff2
            if waiting_dict is not None and updated_peptide2[-1] in 'KR':
                waiting_dict[updated_peptide2] = mass_diff2

    if waiting_dict is not None:
        return mass_diff_dict, results, waiting_dict
    return mass_diff_dict, results


def create_new_mass_dict(mass_diff_dict, next_aa, prepend):
    """ Function to create a new mass difference dictionary of extended
        tags mapped to their mass diff.
    """
    new_mass_diff_dict= {}
    for updated_peptide, mass_diff in mass_diff_dict.items():
        if prepend:
            new_mass_diff_dict[next_aa + updated_peptide] = mass_diff - RESIDUE_WEIGHTS_MOD[next_aa]
        else:
            new_mass_diff_dict[updated_peptide + next_aa] = mass_diff - RESIDUE_WEIGHTS_MOD[next_aa]

        if next_aa == 'M':
            if prepend:
                new_pep = 'm' + updated_peptide
            else:
                new_pep = updated_peptide + 'm'
            new_mass_diff_dict[new_pep] = (
                mass_diff - (RESIDUE_WEIGHTS_MOD[next_aa]+MOD_WEIGHTS['+16.0'])
            )

    return new_mass_diff_dict


def get_relevant_proteins(df, proteome, column, prefix=''):
    """ Function to extract protein sequences with ID found in a df column.
    """
    if df[column].dtype == pl.String:
        proteins = set(df[column].unique().to_list())
    else:
        proteins = set(df[column].explode().unique().to_list())
    relevant_proteins = {}
    protein_name = ''
    active = False
    with open(proteome, mode='r', encoding='UTF-8') as in_file:
        while line := in_file.readline():
            if line.startswith('>'):
                protein_name = prefix + line[1:].strip('\n')
                if protein_name in proteins or line[1:].strip('\n') in proteins:
                    relevant_proteins[protein_name] = ''
                    active = True
                else:
                    active = False
            else:
                if active:
                    relevant_proteins[protein_name] += line.strip('\n')

    if prefix.startswith('rev_'):
        for protein_name in relevant_proteins:
            relevant_proteins[protein_name] = relevant_proteins[protein_name][::-1]

    return relevant_proteins


def write_prot_fasta(total_df, config, label, prefix, db, file_name, mode='w'):
    """ Function to write a fasta file of de novo filtered proteins.
    """
    filt_df = total_df.filter(
        pl.col('proteins').str.contains('CONTAMS').not_() &
        pl.col('Label').eq(label)
    )
    found_prots = get_relevant_proteins(
        filt_df.with_columns(pl.col('proteins').str.split(' ')),
        db, 'proteins', prefix=prefix,
    )
    with open(f'{config.output_folder}/{file_name}.fasta', mode, encoding='UTF-8') as fasta_file:
        for prot_id, prot_seq in found_prots.items():
            fasta_file.write(f'>{prot_id}\n{prot_seq}\n')
