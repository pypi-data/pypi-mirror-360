""" Functions for finding junction peptides in the target proteome.
"""
import multiprocessing as mp
import re

import polars as pl

from pisces.construct_proteome_utils import get_relevant_proteins
from pisces.proteome_utils import distribute_mapping

EXTENSION_COLUMNS = [
    'extensionNName', 'extensionNSeq', 'extendedNProt', 'extendedNEvidence',
    'extensionCName', 'extensionCSeq', 'extendedCProt', 'extendedCEvidence',
]

def find_junction_peptides(config):
    """ Function to find the junction peptides, filter the proteins
        that are now redundant in the target dataframe and return
        the final proteins with junction peptides.
    """
    prot_df = fetch_direct_mapped_proteins(config)
    junction_proteins = []
    for prefix in ['', 'rev_']:
        unique_unmapped_df = get_high_scored_unmapped_peptides(config)
        unique_unmapped_df = get_peptide_substrings(unique_unmapped_df)

        # Find peptides where the majority of the peptide maps to a single protein.
        # We do not search for a peptide fragment that is too short.
        extension_df, unique_unmapped_df = map_shortened_peptides(
            unique_unmapped_df, config, prefix
        )
        extension_df = finalise_extension_proteins(extension_df, config, prefix)
        extension_df = combine_extensions_with_direct_peptides(
            extension_df, prot_df.select(['proteins', 'directPeptides']), prefix
        )

        if not prefix:
            # For target extensions write the extension dataframe to the output folder
            extension_df.write_parquet(f'{config.output_folder}/extension_df_target.parquet')

        junction_df = map_true_junction_peptides(unique_unmapped_df, config, prefix)
        junction_df = junction_df.with_columns(
            pl.struct(['Njunct_Proteins', 'Cjunct_Proteins']).map_elements(
                lambda x : filter_junction_matches(
                    x['Njunct_Proteins'], x['Cjunct_Proteins']
                ),
                return_dtype=pl.List(pl.List(pl.String)),
            ).alias('junctionProteins')
        )
        junction_df = junction_df.explode(['junctionProteins']).drop_nulls()

        if junction_df.shape[0]:
            junction_df = finalise_junction_proteins(junction_df, config, prefix)
            junction_df = combine_junctions_with_direct_peptides(
                junction_df, prot_df.select(['proteins', 'directPeptides'])
            )
        else:
            junction_df = pl.DataFrame({
                'junctionName': [],
                'junctionSeq': [],
            })
            junction_df = junction_df.with_columns(
                pl.col('junctionName').cast(pl.String),
                pl.col('junctionSeq').cast(pl.String),
            )

        if not prefix:
            junction_df.write_parquet(f'{config.output_folder}/junction_df.parquet')
            final_prot_df = select_final_proteins(prot_df, junction_df, extension_df)
            junction_proteins.append(final_prot_df)
        else:
            final_prot_df = pl.concat([
                junction_df.rename(
                    {'junctionName': 'proteins', 'junctionSeq': 'protSeqs'}
                ).select(['proteins', 'protSeqs']),
                extension_df.rename(
                    {'extensionName': 'proteins', 'extensionSeq': 'protSeqs'}
                ).select(['proteins', 'protSeqs']),
            ])

            junction_proteins.append(final_prot_df)

    return pl.concat(junction_proteins)


def get_high_scored_unmapped_peptides(config):
    """ Function to retrieve confident, top ranked peptides without modifications
        that are not mapped to any protein.
    """
    fdr_estimated_df = pl.read_csv(f'{config.output_folder}/fdr_est_data.csv')
    fdr_estimated_df = fdr_estimated_df.with_columns(
        pl.col('source').cast(pl.String)
    )

    # Select only high-scored peptides, long enough and not containing
    # certain modifications
    fdr_estimated_df = fdr_estimated_df.filter(
        (
            (pl.col('piscesScore').gt(0.8) & pl.col('peptide').str.len_chars().ge(12)) |
            (pl.col('piscesScore').gt(0.75) & pl.col('peptide').str.len_chars().ge(20))
        ) &
        pl.col('modifiedSequence').str.contains('17').not_() &
        pl.col('modifiedSequence').str.contains('25').not_() &
        pl.col('modifiedSequence').str.contains('42').not_() &
        pl.col('modifiedSequence').str.contains('43').not_()
    )

    remapped_psms_df = pl.read_csv(
        f'{config.output_folder}/all_remapped_psms.csv'
    )

    # Remove all the remappings for reverse proteins
    remapped_psms_df = remapped_psms_df.with_columns(
        pl.col('proteins').str.split(' '),
    ).explode('proteins')
    remapped_psms_df = remapped_psms_df.filter(
        pl.col('proteins').str.starts_with('rev').not_()
    )

    # Drop candidates if the peptide is already mapped to a protein
    # or if the PSM was not assigned to any other mapped peptide.
    unmapped_df = fdr_estimated_df.join(
        remapped_psms_df.select(['source', 'scan']).unique(),
        how='anti', on=['source', 'scan'],
    )
    unmapped_df = unmapped_df.join(
        remapped_psms_df.select(['peptide']).unique(),
        how='anti', on=['peptide'],
    )

    # Select only the peptide column and remove duplicates
    unmapped_pep_df = unmapped_df.select(['peptide']).unique(
        maintain_order=True
    )
    return unmapped_pep_df


def get_peptide_substrings(unique_unmapped_df):
    """ Function to get the peptide substrings that can be used to find substrings
        that span the junction.
    """
    unique_unmapped_df = unique_unmapped_df.rename({'peptide': 'sourcePeptide'})

    unique_unmapped_df = unique_unmapped_df.with_columns(
        # If a lot of the peptide maps to a single protein then
        # we can only find half the junction peptide.
        pl.col('sourcePeptide').map_elements(
            lambda x : x[:-3] if len(x) >= 9 else '',
            return_dtype=pl.String,
        ).alias('shortenedPeptideN'),
        pl.col('sourcePeptide').map_elements(
            lambda x : x[3:] if len(x) >= 9 else '',
            return_dtype=pl.String,
        ).alias('shortenedPeptideC'),

        # For peptides where both fragments are long enough
        # we can find both halves of the junction peptide.
        pl.col('sourcePeptide').map_elements(
            lambda x : [
                x[:idx] for idx in range(4, len(x)-3)
            ] if len(x) >= 9 else [],
            return_dtype=pl.List(pl.String),
        ).alias('peptideN'),
        pl.col('sourcePeptide').map_elements(
            lambda x : [
                x[idx:] for idx in range(4, len(x)-3)
            ] if len(x) >= 9 else [],
            return_dtype=pl.List(pl.String),
        ).alias('peptideC'),
        pl.col('sourcePeptide').map_elements(
            lambda x : list(range(4, len(x)-3)) if len(x) >= 9 else [],
            return_dtype=pl.List(pl.Int64),
        ).alias('cutIdx'),
    )
    return unique_unmapped_df


def map_shortened_peptides(unique_unmapped_df, config, prefix):
    """ Function to map the shortened peptides to the target proteome.
    """
    for code, col in zip(
        ['shortenedN', 'shortenedC'],
        ['shortenedPeptideN', 'shortenedPeptideC']
    ):
        renamed_df = unique_unmapped_df.rename({col: 'peptide'})
        fuzzy_matched_df = distribute_mapping(
            renamed_df,
            f'{config.output_folder}/direct_mappings_target.fasta',
            f'{code}',
            config.n_cores,
            with_splicing=False,
            max_intervening=config.max_intervening,
            prefix=prefix,
            tree_size=config.tree_size,
        )
        unique_unmapped_df = unique_unmapped_df.join(
            fuzzy_matched_df, how='left', left_on=col, right_on='peptide', #coalesce=True,
        )
        unique_unmapped_df = unique_unmapped_df.drop('peptide')

    extension_df = unique_unmapped_df.filter(
        pl.col('shortenedN_nProteins').gt(0) |
        pl.col('shortenedC_nProteins').gt(0)
    ).drop(['shortenedN_nProteins', 'shortenedC_nProteins'])
    unique_unmapped_df = unique_unmapped_df.filter(
        pl.col('shortenedN_nProteins').eq(0) &
        pl.col('shortenedC_nProteins').eq(0)
    ).drop([
        'shortenedN_nProteins', 'shortenedC_nProteins',
        'shortenedN_Proteins', 'shortenedC_Proteins'
    ])

    return extension_df, unique_unmapped_df

def map_true_junction_peptides(unique_unmapped_df, config, prefix):
    """ Function to map the junction peptides which have both N and C terminus
        mapped to the target proteome.
    """
    unique_unmapped_df = unique_unmapped_df.explode(['peptideN', 'peptideC', 'cutIdx'])
    unique_unmapped_df = unique_unmapped_df.drop_nulls()
    for code, col in zip(['Njunct', 'Cjunct'], ['peptideN', 'peptideC']):
        renamed_df = unique_unmapped_df.rename({col: 'peptide'})
        fuzzy_matched_df = distribute_mapping(
            renamed_df,
            f'{config.output_folder}/direct_mappings_target.fasta',
            f'{code}',
            config.n_cores,
            with_splicing=False,
            max_intervening=config.max_intervening,
            prefix=prefix,
            tree_size=config.tree_size,
        )

        unique_unmapped_df = unique_unmapped_df.join(
            fuzzy_matched_df, how='left', left_on=col, right_on='peptide',
        )
        unique_unmapped_df = unique_unmapped_df.drop('peptide')

    junction_df = unique_unmapped_df.filter(
        pl.col('Njunct_nProteins').gt(0) &
        pl.col('Cjunct_nProteins').gt(0)
    )
    junction_df = junction_df.with_columns(
        pl.col('Njunct_Proteins').str.split(' '),
        pl.col('Cjunct_Proteins').str.split(' '),
    )
    return junction_df

def filter_junction_matches(prot_list1, prot_list2):
    """ Function to filter the junction matches based on whether
        the junction fragments are from the same chromosome and
        direction and within 1_000_000 nucleotides of one another.
    """
    matched_prots = []
    for prot1 in prot_list1:
        for prot2 in prot_list2:
            if not prot1 or not prot2:
                continue
            pos_prot1 = int(prot1.split('_index_')[-1])
            pos_prot2 = int(prot2.split('_index_')[-1])
            if abs(pos_prot1 - pos_prot2) > 1_000_000:
                continue
            if prot1.split('_index')[0][:-2] == prot2.split('_index')[0][:-2]:
                matched_prots.append([prot1, prot2])

    return matched_prots

def create_junction_seq(prot_list, prot_seq_list, pep_n, pep_c, source_pep):
    """ Function to create the junction sequence from the peptide fragments.
    """
    if pep_n + pep_c != source_pep:
        print(pep_n, pep_c, source_pep)
        raise ValueError(
            f'Peptide N and C terminus do not match source peptide {pep_n}, {pep_c}, {source_pep}.'
        )
    n_term_idx = 0
    n_term_inds = [
        match.start() for match in re.finditer(pep_n, prot_seq_list[0].replace('I', 'L'))
    ]
    for idx in n_term_inds[::-1]:
        if prot_seq_list[0][idx - 1] in 'KR':
            n_term_idx = idx
            break

    c_term_idx = prot_seq_list[1].replace('I', 'L').index(pep_c)
    n_term = prot_seq_list[0][:n_term_idx + len(pep_n)]
    if not n_term_idx or (
        prot_seq_list[0][n_term_idx - 1] not in 'KR'
    ) or (
        c_term_idx + len(pep_c) == len(prot_seq_list[1])
    ):
        return {
            'junctionName': None,
            'junctionSeq': None,
            'N_junct_Proteins': None,
            'C_junct_Proteins': None,
        }
    c_term = prot_seq_list[1][c_term_idx:]
    junction_seq = f'{n_term}{c_term}'
    junction_name = f'junction|{prot_list[0]}|{pep_n}|{prot_list[1]}|{pep_c}|{source_pep}'
    return {
        'junctionName': junction_name,
        'junctionSeq': junction_seq,
        'N_junct_Proteins': prot_list[0],
        'C_junct_Proteins': prot_list[1],
    }



def finalise_extension_proteins(extension_df, config, prefix):
    """ Function to take the final approved extension peptides.
    """
    sub_dfs =[]
    for col, code in zip(['shortenedN_Proteins', 'shortenedC_Proteins'], ['N', 'C']):
        seq_col = col.replace('Proteins', 'ProtSeqs')
        sub_df = extension_df.with_columns(
            pl.col(col).str.split(' '),
        ).explode(col)
        relevant_proteins = get_relevant_proteins(
            sub_df,
            f'{config.output_folder}/direct_mappings_target.fasta',
            col,
            prefix=prefix,
        )
        sub_df = sub_df.filter(pl.col(col).ne(''))
        sub_df = sub_df.with_columns(
            pl.col(col).map_dict(relevant_proteins).alias(seq_col)
        )

        sub_df = sub_df.drop_nulls([seq_col])
        sub_df = sub_df.with_columns(
            pl.struct([
                    col, seq_col, 'sourcePeptide'
                ]).map_elements(
                    lambda x : create_extension_seq(
                        x[col], x[seq_col], x['sourcePeptide'], code, prefix
                    ),
                    return_dtype=pl.Struct(
                        [
                            pl.Field(f'extension{code}Name', pl.String),
                            pl.Field(f'extension{code}Seq', pl.String),
                            pl.Field(f'extended{code}Prot', pl.String),
                            pl.Field(f'extended{code}Evidence', pl.Int64),
                        ]
                    ),
            ).alias(f'extension{code}Results')
        )
        sub_df = sub_df.unnest(f'extension{code}Results')
        sub_dfs.append(sub_df)


    # Combined N extended and C extended, if there is a case where a peptide has N and C terminal
    # extensions, we take the one with the highest evidence score.
    extension_df = sub_dfs[0].select(
        ['sourcePeptide', 'extensionNName', 'extensionNSeq',
        'extendedNProt', 'extendedNEvidence',]
    ).join(
        sub_dfs[1].select(
            [
                'sourcePeptide', 'extensionCName', 'extensionCSeq',
                'extendedCProt', 'extendedCEvidence'
            ]
        ),
        how='outer_coalesce', on='sourcePeptide',
    )
    extension_df = extension_df.with_columns(
        pl.struct(EXTENSION_COLUMNS).map_elements(
            lambda x : select_extension_proteins(*[x[col] for col in EXTENSION_COLUMNS]),
            return_dtype=pl.Struct(
                [
                    pl.Field('extensionName', pl.String),
                    pl.Field('extensionSeq', pl.String),
                    pl.Field('extendedProt', pl.String),
                    pl.Field('extendedEvidence', pl.Int64),
                ]
            ),
        ).alias('extensionResults')
    )
    extension_df = extension_df.unnest('extensionResults')
    extension_df = extension_df.sort(
        ['sourcePeptide', 'extendedEvidence'], descending=[False, True],
    )
    extension_df = extension_df.unique(['sourcePeptide'], maintain_order=True)
    extension_df = extension_df.drop(EXTENSION_COLUMNS)

    extension_df = extension_df.filter(
        pl.col('extensionSeq').str.len_chars().gt(20)
    )
    return extension_df

def select_extension_proteins(
    extension_n_name, extension_n_seq, extended_n_prot, extended_n_evidence,
    extension_c_name, extension_c_seq, extended_c_prot, extended_c_evidence,
):
    """ Function to select the most suitable extension peptide.
    """
    if extension_n_name is None:
        return {
            'extensionName': extension_c_name,
            'extensionSeq': extension_c_seq,
            'extendedProt': extended_c_prot,
            'extendedEvidence': extended_c_evidence,
        }
    if extension_c_name is None:
        return {
            'extensionName': extension_n_name,
            'extensionSeq': extension_n_seq,
            'extendedProt': extended_n_prot,
            'extendedEvidence': extended_n_evidence,
        }
    if extended_n_evidence > extended_c_evidence:
        return {
            'extensionName': extension_n_name,
            'extensionSeq': extension_n_seq,
            'extendedProt': extended_n_prot,
            'extendedEvidence': extended_n_evidence,
        }
    return {
        'extensionName': extension_c_name,
        'extensionSeq': extension_c_seq,
        'extendedProt': extended_c_prot,
        'extendedEvidence': extended_c_evidence,
    }

def create_extension_seq(prot_name, prot_seq, source_pep, code, prefix):
    """ Function to create an extended protein sequence to fit a peptide.
    """
    prot_idx = 0
    pep_idx = 0
    il_prot = prot_seq.replace('I', 'L')
    if code == 'N':
        for idx in [1, 2, 3]:
            sub_pep = source_pep[:-idx]
            n_term_inds = [
                match.start() for match in re.finditer(sub_pep, il_prot)
            ]
            for match_idx in n_term_inds[::-1]:
                if prot_seq[match_idx - 1] in 'KR':
                    pep_idx = idx
                    prot_idx = match_idx
                    break
            if pep_idx:
                break
    else:
        for idx in [1, 2, 3]:
            sub_pep = source_pep[idx:]
            if sub_pep in il_prot:
                prot_idx = il_prot.index(sub_pep)
                pep_idx = idx
                break

    if not prot_idx and not pep_idx:
        return {
            f'extension{code}Name': None,
            f'extension{code}Seq': None,
            f'extended{code}Prot': None,
            f'extended{code}Evidence': 0,
        }

    if code == 'N':
        pos_on_pep = len(source_pep) - pep_idx
        extension_seq = f'{prot_seq[:prot_idx+pos_on_pep]}{source_pep[pos_on_pep:]}'
        extension_name = (
            f'{prefix}extension{code}|{prot_name}|{prot_idx}|' +
            f'{source_pep}|{len(source_pep) - pep_idx}'
        )
    else:
        extension_seq = f'{source_pep[:pep_idx]}{prot_seq[prot_idx:]}'
        extension_name = f'{prefix}extension{code}|{source_pep}|{pep_idx}|{prot_name}|{prot_idx} '

    return {
        f'extension{code}Name': extension_name,
        f'extension{code}Seq': extension_seq,
        f'extended{code}Prot': prot_name,
        f'extended{code}Evidence': (len(source_pep) - pep_idx) + int(code == 'N'),
    }


def finalise_junction_proteins(junction_df, config, prefix):
    """ Function to finalise the selection of junction peptides and create the
        junction sequence.
    """
    relevant_proteins = get_relevant_proteins(
        junction_df,
        f'{config.output_folder}/direct_mappings_target.fasta',
        'junctionProteins',
        prefix=prefix,
    )
    junction_df = junction_df.with_columns(
        pl.col('junctionProteins').map_elements(
            lambda x : [relevant_proteins[y] for y in x],
            return_dtype=pl.List(pl.String),
        ).alias('junctionProtSeqs')
    )
    junction_df = junction_df.with_columns(
        pl.struct(
            [
                'junctionProteins', 'junctionProtSeqs', 'peptideN',
                'peptideC', 'sourcePeptide'
            ]).map_elements(
                lambda x : create_junction_seq(
                    x['junctionProteins'], x['junctionProtSeqs'], x['peptideN'],
                    x['peptideC'], x['sourcePeptide']
                ),
                return_dtype=pl.Struct([
                    pl.Field('junctionName', pl.String),
                    pl.Field('junctionSeq', pl.String),
                    pl.Field('N_junct_Proteins', pl.String),
                    pl.Field('C_junct_Proteins', pl.String),
                ]),
        ).alias('junctionResults')
    )
    junction_df = junction_df.unnest('junctionResults')
    junction_df = junction_df.drop_nulls(['junctionName', 'junctionSeq'])
    return junction_df


def fetch_direct_mapped_proteins(config):
    """ Function to fetch proteins which have direct mapping peptides assigned.
    """
    remapped_psms_df = pl.read_csv(f'{config.output_folder}/all_remapped_psms.csv')
    remapped_psms_df = remapped_psms_df.with_columns(
        pl.col('proteins').str.split(' '),
    ).explode('proteins')
    remapped_psms_df = remapped_psms_df.filter(pl.col('proteins').str.len_chars() != 0)
    remapped_psms_df = remapped_psms_df.sort('Score', descending=True)
    remapped_psms_df = remapped_psms_df.select(['proteins', 'peptide', 'Score']).unique(
        subset=['proteins', 'peptide'],
        maintain_order=True,
    )
    prot_df = remapped_psms_df.group_by('proteins').agg(
        pl.col('peptide').alias('directPeptides'),
        # pl.col('Score').alias('directScores'),
    )
    prot_df = prot_df.filter(
        pl.col('proteins').str.starts_with('rev').not_() &
        pl.col('proteins').str.contains('CONTAMS').not_()
    )
    relevant_proteins = get_relevant_proteins(
        prot_df,
        f'{config.output_folder}/direct_mappings_target.fasta',
        'proteins',
    )
    prot_df = prot_df.with_columns(
        pl.col('proteins').map_dict(relevant_proteins).alias('protSeqs')
    )

    return prot_df


def combine_dfs(junction_df, extension_df):
    """ Function to combine the junction and extension dataframes
    """
    exon_1_2_df = junction_df.select(
        [
            'junctionName', 'N_junct_Proteins', 'C_junct_Proteins',
            'junctionSeq', 'mappedPeptides', 'peptideC', 'sourcePeptide'
        ]
    ).rename({
        'junctionName': 'junctionName_1_2', 'N_junct_Proteins': 'exon1',
        'C_junct_Proteins': 'exon2', 'junctionSeq': 'exon1_2_seq',
        'mappedPeptides': 'mappedPeptides_1_2', 'peptideC': 'peptideN_2',
        'sourcePeptide': 'sourcePeptide_12',
    })
    exon_2_3_df = junction_df.select([
        'junctionName', 'N_junct_Proteins', 'C_junct_Proteins', 'junctionSeq', 'mappedPeptides',
        'peptideN', 'sourcePeptide'
    ]).rename({
        'junctionName': 'junctionName_2_3', 'N_junct_Proteins': 'exon2',
        'C_junct_Proteins': 'exon3', 'junctionSeq': 'exon2_3_seq',
        'mappedPeptides': 'mappedPeptides_2_3', 'peptideN': 'peptideC_2',
        'sourcePeptide': 'sourcePeptide_23',
    })

    multi_exon_df = exon_1_2_df.join(exon_2_3_df, how='inner', on=['exon2'])

    multi_exon_df = multi_exon_df.filter(
        pl.col('sourcePeptide_12').ne(pl.col('sourcePeptide_23')) &
        pl.col('sourcePeptide_12').str.contains(pl.col('sourcePeptide_23')).not_() &
        pl.col('sourcePeptide_23').str.contains(pl.col('sourcePeptide_12')).not_()
    )

    multi_exon_df = multi_exon_df.with_columns(
        pl.struct([
            'exon1_2_seq', 'exon2_3_seq', 'peptideN_2', 'peptideC_2',
            'sourcePeptide_12', 'sourcePeptide_23'
        ]).map_elements(
            lambda x : combined_junctions(
                x['exon1_2_seq'], x['exon2_3_seq'], x['peptideN_2'],
                x['peptideC_2'], x['sourcePeptide_12'],x['sourcePeptide_23']
            ),
        ).alias('multiExonSeq')
    )

    multi_exon_df = multi_exon_df.with_columns(
        pl.struct(['multiExonSeq', 'mappedPeptides_1_2', 'mappedPeptides_2_3']).map_elements(
            lambda x : list(set(
                [y for y in x['mappedPeptides_1_2'] if y in x['multiExonSeq'].replace('I', 'L')] +
                [y for y in x['mappedPeptides_2_3'] if y in x['multiExonSeq'].replace('I', 'L')]
            )),
        ).alias('mappedPeptides'),
        pl.struct(['multiExonSeq', 'mappedPeptides_1_2', 'mappedPeptides_2_3']).map_elements(
            lambda x : list(set(
                [y for y in x['mappedPeptides_1_2'] if y not in x['multiExonSeq'].replace('I', 'L')] +
                [y for y in x['mappedPeptides_2_3'] if y not in x['multiExonSeq'].replace('I', 'L')]
            )),
        ).alias('lostPeptides'),
    )

def combined_junctions(exon1_2_seq, exon2_3_seq, peptide_key):
    """ Function to combine the junction sequences from exon 1-2 and exon 2-3
    """
    exon1_2_cut = [
        match.start() for match in re.finditer(peptide_key, exon1_2_seq.replace('I', 'L'))
    ][-1]
    exon1_2_seq_trimmed = exon1_2_seq[:exon1_2_cut]

    exon2_3_cut = exon2_3_seq.replace('I', 'L').index(peptide_key)
    exon2_3_seq_trimmed = exon2_3_seq[exon2_3_cut:]

    junction_seq = exon1_2_seq_trimmed + exon2_3_seq_trimmed

    return junction_seq


def select_final_proteins(prot_df, junction_df, extension_df):
    """ Function to select the final proteins with junctions and extensions,
    """
    prot_seq_df = pl.concat([
        prot_df.select(['proteins', 'protSeqs']),
        junction_df.rename(
            {'junctionName': 'proteins', 'junctionSeq': 'protSeqs'}
        ).select(['proteins', 'protSeqs']),
        extension_df.rename(
            {'extensionName': 'proteins', 'extensionSeq': 'protSeqs'}
        ).select(['proteins', 'protSeqs']),
    ])
    total_df = pl.concat([
        prot_df.rename({'directPeptides': 'mappedPeptides'}).select(['proteins', 'mappedPeptides']),
        junction_df.rename({
            'junctionName': 'proteins'
        }).select(['proteins', 'mappedPeptides']),
        extension_df.rename({'extensionName': 'proteins'}).select(['proteins', 'mappedPeptides']),
    ])

    total_df = total_df.explode('mappedPeptides')

    total_df = total_df.with_columns(
        pl.col('mappedPeptides').str.to_uppercase(),
    )

    total_df = total_df.unique()
    total_df = total_df.with_columns(
        pl.col('proteins').n_unique().over('mappedPeptides').alias('proteinsCount'),
        pl.col('mappedPeptides').n_unique().over('proteins').alias('peptidesCount'),
    )

    unique_df = total_df.filter(
        pl.col('proteinsCount').eq(1)
    )

    unique_df = unique_df.group_by('proteins').agg(
        pl.col('mappedPeptides').n_unique().alias('uniquePeptidesCount'),
    )
    total_df = total_df.join(
        unique_df.select(['proteins', 'uniquePeptidesCount']),
        how='left', on=['proteins'],
    )
    total_df = total_df.with_columns(
        pl.col('uniquePeptidesCount').fill_null(0),
    )
    total_df = total_df.with_columns(
        pl.col('uniquePeptidesCount').max().over('mappedPeptides').alias('maxUniqueProteins'),
    )

    total_df = total_df.filter(pl.col('uniquePeptidesCount').eq(pl.col('maxUniqueProteins')))
    total_df = total_df.select(['proteins']).unique().join(prot_seq_df, how='inner', on='proteins')
    return total_df.sort('proteins')


def score_extension_matches(source_peptide, extension_seq, direct_peps):
    """ Function to find the number of peptides lost and stil supporting an extension
        sequence.
    """
    extension_seq_il = extension_seq.replace('I', 'L')
    extension_score = 1
    mapped_peps = [source_peptide]
    lost_peps = 0

    for pep in direct_peps:
        if pep in extension_seq_il:
            extension_score += 1
            mapped_peps.append(pep)
        else:
            lost_peps += 1

    return {
        'extendedProtScore': extension_score,
        'mappedPeptides': mapped_peps,
        'lostPeptides': lost_peps,
    }


def combine_extensions_with_direct_peptides(extension_df, prot_df, prefix):
    """ Function to combine the extension proteins with the direct mapped peptides.
    """
    prot_df = prot_df.with_columns(
        (prefix + pl.col('proteins')).alias('proteins')
    )
    extension_df = extension_df.join(
        prot_df, how='inner', left_on='extendedProt', right_on='proteins'
    ).drop('proteins')
    extension_df = extension_df.with_columns(
        pl.struct([
            'extensionSeq', 'directPeptides', 'sourcePeptide',
        ]).map_elements(
            lambda x : score_extension_matches(
                x['sourcePeptide'], x['extensionSeq'], x['directPeptides'],
            ),
            return_dtype=pl.Struct(
                [pl.Field('extendedProtScore', pl.Int64),
                pl.Field('mappedPeptides', pl.List(pl.String)),
                pl.Field('lostPeptides', pl.Int64)
                ],
            ),
        ).alias('extensionResults')
    )
    extension_df = extension_df.unnest('extensionResults')
    return extension_df


def combine_junctions_with_direct_peptides(junction_df, prot_df):
    """ Function to combine junction peptides with the peptides which directly
        map for the joined proteins
    """
    junction_df = junction_df.join(
        prot_df, how='inner', left_on='N_junct_Proteins', right_on='proteins'
    ).drop('proteins').rename({'directPeptides': 'N_junct_peptides'})
    junction_df = junction_df.join(
        prot_df, how='inner', left_on='C_junct_Proteins', right_on='proteins'
    ).drop('proteins').rename({'directPeptides': 'C_junct_peptides'})

    junction_df = junction_df.with_columns(
        pl.struct([
            'sourcePeptide', 'cutIdx', 'junctionSeq',
            'N_junct_peptides', 'C_junct_peptides'
        ]).map_elements(
            lambda x : score_junction_matches(
                x['sourcePeptide'], x['cutIdx'], x['junctionSeq'],
                x['N_junct_peptides'], x['C_junct_peptides']
            ),
            return_dtype=pl.Struct(
                [pl.Field('junctionScore', pl.Int64),
                pl.Field('mappedPeptides', pl.List(pl.String)),
                pl.Field('lostPeptides', pl.Int64),
                pl.Field('minTag', pl.Int64)],
            ),
        ).alias('junctionResults')
    )
    junc_peps = sorted(
        list(set(junction_df['sourcePeptide'].unique().to_list()))
    )
    junction_df = junction_df.with_columns(
        pl.col('sourcePeptide').map_elements(
            lambda x : max([x in y for y in junc_peps if y != x]),
            return_dtype=pl.Boolean,
        ).alias('isSubstring'),
        pl.col('sourcePeptide').map_elements(
            lambda x : [y for y in junc_peps if y in x and y != x],
            return_dtype=pl.List(pl.String),
        ).alias('substrings')
    )
    junction_df = junction_df.unnest('junctionResults')
    junction_df = junction_df.sort(
        ['sourcePeptide', 'junctionScore', 'lostPeptides', 'minTag'],
        descending=[False, True, False, True]
    )
    junction_df = junction_df.unique(['sourcePeptide'], maintain_order=True)
    junction_df = junction_df.filter(pl.col('isSubstring').not_())
    junction_df = junction_df.with_columns(
        pl.concat_list('mappedPeptides', 'substrings').alias('mappedPeptides')
    )
    junction_df = junction_df.with_columns(
        (
            pl.col('junctionScore') + pl.col('substrings').list.len()
        ).alias('junctionScore'),
    )

    return junction_df


def score_junction_matches(
    source_pep, cut_idx, junction_seq, n_junct_peptides, c_junct_peptides
):
    """ Function to score the junction matches based on the peptides matched.
    """
    junction_seq_il = junction_seq.replace('I', 'L')
    junction_score = 1
    lost_peps = 0
    mapped_peps = [source_pep]

    for pep in n_junct_peptides:
        if pep in junction_seq_il:
            junction_score += 1
            mapped_peps.append(pep)
        else:
            lost_peps += 1

    for pep in c_junct_peptides:
        pep = pep.replace('I', 'L')
        if pep in junction_seq_il:
            junction_score += 1
            mapped_peps.append(pep)
        else:
            lost_peps += 1

    return {
        'junctionScore': junction_score,
        'mappedPeptides': mapped_peps,
        'lostPeptides': lost_peps,
        'minTag': min([cut_idx, len(source_pep) - cut_idx]),
    }
