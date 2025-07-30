""" Functions for finding additional contaminant peptides.
"""
import os
from pathlib import Path
from inspire.utils import fetch_proteome
import pandas as pd
import polars as pl

from pisces.download_swissprot import download_swissprot_match
from pisces.remap import process_fasta_folder

def check_contaminants(config, remapped_df, cryptic_strata):
    """ Function to check for contaminant peptides.
    """
    jar_path, sprot_path = download_swissprot_match()
    drop_cryptic = False
    if 'nCrypticProteins' not in remapped_df.columns:
        remapped_df = remapped_df.with_columns(
            pl.lit(0).alias('nCrypticProteins'),
        )
        drop_cryptic = True
    unmapped_df = remapped_df.filter(
        pl.col('canonical_nProteins').eq(0) &
        pl.col('nContamProteins').eq(0) &
        pl.col('nSplicedProteins').eq(0) &
        pl.col('nCrypticProteins').eq(0)
    ).to_pandas()
    unmapped_df = unmapped_df[unmapped_df['qValue_PSM'] < 0.05]

    unmapped_pep_path = f'{config.output_folder}/holdingFolder/uniprot_query.list'
    unmapped_df[['peptide']].drop_duplicates().to_csv(
        unmapped_pep_path, index=False, header=False
    )

    out_path = f'{config.output_folder}/details/uniprot_query_results.list'
    os.system(
        f'java -jar {jar_path} -a query -i {sprot_path} -Q ' +
        f'{unmapped_pep_path} -l -e -o {out_path}'
    )

    search_res_df, potential_organisms = map_peptides_to_organisms(out_path)
    organism_df = None
    if search_res_df is not None:
        organism_df = get_organism_df(search_res_df, potential_organisms)

    if organism_df is None:
        organism_list = []
    else:
        organism_df = get_final_count(organism_df, search_res_df)
        organism_df.to_csv(f'{config.output_folder}/details/full_organism_counts.csv', index=False)
        organism_df = organism_df[organism_df['trueCount'] > 2]
        organism_list = organism_df['organism'].tolist()

    if organism_list:
        contam_org_folder = f'{config.output_folder}/details/contamOrganisms'
        download_organisms(organism_list, contam_org_folder)


        remapped_df, _ = process_fasta_folder(
            remapped_df,
            contam_org_folder,
            config.n_cores,
            config.output_folder,
            'specific_contams',
        )
        remapped_df = remapped_df.with_columns(
            pl.struct(['nSplicedProteins', 'nSpecific_ContamsProteins']).map_elements(
                lambda x : x['nSplicedProteins'] if x['nSpecific_ContamsProteins'] == 0 else 0
            ).alias('nSplicedProteins'),
            pl.struct(['nCrypticProteins', 'nSpecific_ContamsProteins']).map_elements(
                lambda x : x['nCrypticProteins'] if x['nSpecific_ContamsProteins'] == 0 else 0
            ).alias('nCrypticProteins'),
        )
        for strat_name in cryptic_strata:
            remapped_df = remapped_df.with_columns(
                pl.struct([f'{strat_name}_nProteins', 'nSpecific_ContamsProteins']).map_elements(
                    lambda x : (
                        x[f'{strat_name}_nProteins'] if x['nSpecific_ContamsProteins'] == 0 else 0
                    ),
                    return_dtype=pl.Int64,
                ).alias(f'{strat_name}_nProteins'),
            )
    else:
        remapped_df = remapped_df.with_columns(
            pl.lit(0).alias('nSpecific_ContamsProteins')
        )

    if drop_cryptic:
        remapped_df = remapped_df.drop('nCrypticProteins')

    return remapped_df


def download_organisms(organism_list, contam_org_folder):
    """ Functio
    """
    if not os.path.exists(contam_org_folder):
        os.mkdir(contam_org_folder)

    organism_files = {}
    for organism in organism_list:
        safe_organism = organism.replace('/', '').replace('.', '')
        organism_files[organism] = open(
            f'{contam_org_folder}/{safe_organism}.fasta', 'w', encoding='UTF-8',
        )

    home = str(Path.home())
    proteome = fetch_proteome(
        f'{home}/inSPIRE_models/uniprot_sprot.fasta', with_desc=True
    )
    for prot in proteome:
        for organism in organism_list:
            if organism in prot[2]:
                organism_files[organism].write(
                    f'>{prot[0]}\n{prot[1]}\n'
                )

    for org_file in organism_files.values():
        org_file.close()


def map_peptides_to_organisms(out_path):
    """ Function all organisms for each peptide.
    """
    search_res_df = pd.read_csv(
        out_path, skiprows=[0], sep='\t'
    )
    search_res_df = search_res_df.rename(columns={
        '##Query': 'peptide', 'Subject': 'protein',
    })
    search_res_df = search_res_df[['peptide', 'protein']].drop_duplicates()

    # Match proteins to organism:

    home = str(Path.home())
    proteome = fetch_proteome(
        f'{home}/inSPIRE_models/uniprot_sprot.fasta', with_desc=True
    )
    org_data = []
    for prot in proteome:
        org_data.append({
            'protein': prot[0],
            'organism': prot[2].split('OS=')[-1].split(' OX=')[0],
        })
    prot_org_df = pd.DataFrame(org_data)
    search_res_df = pd.merge(search_res_df, prot_org_df, how='left', on='protein')

    # Define column per organism if the peptide could originate in that organism:
    potential_organisms = sorted([
        x for x in search_res_df['organism'].unique().tolist() if isinstance(x, str)
    ])
    search_res_df = search_res_df.groupby('peptide', as_index=False)['organism'].apply(list)
    for organism in potential_organisms:
        search_res_df[organism] = search_res_df['organism'].apply(
            lambda x : 0 if not isinstance(x[0], str) else (1 if organism in x else 0)
        )

    if not search_res_df.shape[0]:
        return None, []
    # Define total number of possible organisms and filter fully unmapped peptides
    search_res_df['totalOrganisms'] = search_res_df[potential_organisms].apply(sum, axis=1)
    search_res_df = search_res_df[search_res_df['totalOrganisms'] > 0]

    return search_res_df, potential_organisms

def get_organism_df(search_res_df, potential_organisms):
    """ Get per organism DataFrame of counts.
    """
    organism_res = []
    for organism in potential_organisms:
        org_df = search_res_df[search_res_df[organism] > 0]
        organism_res.append({
            'organism': organism,
            'count': org_df.shape[0],
            'uniqueCount': org_df[org_df['totalOrganisms'] == 1].shape[0],
        })
    if not organism_res:
        return None
    organism_res_df = pd.DataFrame(organism_res)
    organism_res_df = organism_res_df.sort_values(
        by=['uniqueCount', 'count'], ascending=False
    ).reset_index(drop=True)
    return organism_res_df


def get_final_count(organism_df, search_res_df):
    """ Function to get final count of peptides per organism excluding peptides
        from higher ranked organisms.
    """
    final_count_list = []
    for _, df_row in organism_df.iterrows():
        new_count = 0
        organism = df_row['organism']
        rank = int(organism_df[
            (organism_df['count'] == df_row['count']) &
            (organism_df['uniqueCount'] == df_row['uniqueCount'])
        ].index[0])
        higher_ranked_oragnisms = organism_df[organism_df.index < rank]['organism'].tolist()

        organism_search_df = search_res_df[search_res_df[organism] == 1]
        for _, df_row2 in organism_search_df.iterrows():
            if set(df_row2['organism']).intersection(set(higher_ranked_oragnisms)):
                continue
            new_count += 1

        final_count_list.append(new_count)

    organism_df['trueCount'] = final_count_list
    return organism_df
