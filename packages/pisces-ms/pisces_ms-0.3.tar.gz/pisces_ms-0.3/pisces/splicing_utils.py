""" Functions for mapping peptides to the spliced proteome.
"""
import re
import json

from pisces.constants import EMPTY_SPLICING_RESULTS

def check_cis_present(protein, sr_1, sr_2, max_intervening):
    """ Function to check if two splice reactants are present in a proteome with an intervening
        sequence length of 25 or less.

    Parameters
    ----------
    protein : str
        The protein sequence.
    sr_1 : str
        The first splice reactant.
    sr_2 : str
        The second splice reactant.

    Returns
    -------
    is_present : bool
        Flag indicating if the two splice reactants are present with an intervening sequence
        length of max_intervening.
    """
    matches = []
    if sr_1 in protein and sr_2 in protein:
        frag_1_inds = [
            m.start() for m in re.finditer(sr_1, protein)
        ]
        frag_2_inds = [
            m.start() for m in re.finditer(sr_2, protein)
        ]
        for f1_ind in frag_1_inds:
            for f2_ind in frag_2_inds:
                diff = f1_ind - f2_ind
                int_seq_len = abs((f1_ind + len(sr_1)) - f2_ind)
                if diff < 0:
                    if f1_ind + len(sr_1) >= f2_ind:
                        continue
                    if not max_intervening:
                        matches.append((f1_ind, f2_ind, int_seq_len))
                        continue
                else:
                    if f2_ind + len(sr_2) >= f1_ind:
                        continue
                    if not max_intervening:
                        matches.append((f1_ind, f2_ind, int_seq_len))
                        continue

                if int_seq_len <= max_intervening:
                    matches.append((f1_ind, f2_ind, int_seq_len))

    return matches

def remap_to_spliced_proteome(
        peptide,
        accessions,
        proteome,
        trie,
        max_intervening,
    ):
    """ Function to check for the presence of an identified peptide as either canonical
        or spliced in the input proteome.
    """
    splice_reactant_pairs = [
        (peptide[:i], peptide[i:]) for i in range(1, len(peptide))
    ]
    if not accessions:
        accessions = []
    else:
        accessions = json.loads(accessions)


    for (sr_1, sr_2) in splice_reactant_pairs:
        if len(sr_1) < 3:
            potential_prots = {x[0] for x in trie.find_all(sr_2)}
        elif len(sr_2) < 3:
            potential_prots = {x[0] for x in trie.find_all(sr_1)}
        else:
            sr1_prots = {x[0] for x in trie.find_all(sr_1)}
            sr2_prots = {x[0] for x in trie.find_all(sr_2)}
            potential_prots = sr1_prots.intersection(sr2_prots)

        potential_prots = sorted(list(potential_prots))
        for protein_name in potential_prots:
            indices_list = check_cis_present(
                proteome[protein_name], sr_1, sr_2, max_intervening
            )
            indices_list = sorted(indices_list)

            for indices in indices_list:
                acc = {
                    'sr1_Index': str(indices[0]),
                    'sr2_Index': str(indices[1]),
                    'interveningSeqLength': str(abs(indices[2])),
                    'sr1': sr_1,
                    'protName': protein_name,
                    'isForward': str(int(indices[0] < indices[1]))
                }
                accessions.append(acc)

    return json.dumps(accessions)

def combine_accessions(df_row, n_cores):
    """ Function to combine list of accessions to dict.
    """
    accessions = []
    for idx in range(n_cores):
        accessions.extend(json.loads(df_row[f'accession_{idx}']))

    if accessions:
        return {
            'nSplicedProteins': len({acc['protName'] for acc in accessions}),
            'splicedProteins': ' '.join(
                [acc['protName'] for acc in accessions]
            ),
            'sr1_Index': ' '.join([acc['sr1_Index'] for acc in accessions]),
            'sr2_Index': ' '.join([acc['sr2_Index'] for acc in accessions]),
            'sr1': ' '.join([acc['sr1'] for acc in accessions]),
            'interveningSeqLengths': ' '.join(
                [acc['interveningSeqLength'] for acc in accessions]
            ),
            'isForward': ' '.join([acc['isForward'] for acc in accessions]),
        }

    return EMPTY_SPLICING_RESULTS
