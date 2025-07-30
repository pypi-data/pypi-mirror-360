""" Functions for getting top ranked de novo PSMs and the generating delta score.
"""
import pandas as pd

def get_delta_scores(config):
    """ Function to get delta scores.
    """
    all_de_novo_df = pd.read_csv(
        f'{config.output_folder}/all_scored_candidates.csv'
    )
    all_de_novo_df['source'] = all_de_novo_df['source'].astype(str)

    all_de_novo_df['allScanRank'] = all_de_novo_df.groupby(
        ['source', 'scan']
    )['piscesScore1'].transform(
        'rank', method='first', ascending=False,
    )
    top_ranked_df = all_de_novo_df[all_de_novo_df['allScanRank'] == 1]
    second_ranked_df = all_de_novo_df[all_de_novo_df['allScanRank'] == 2].rename(
        columns={
            'piscesScore1': 'rank2score',
            'peptide': 'rank2peptide',
        }
    )
    third_ranked_df = all_de_novo_df[all_de_novo_df['allScanRank'] == 3].rename(
        columns={
            'piscesScore1': 'rank3score',
            'peptide': 'rank3peptide',
        }
    )

    top_ranked_df = pd.merge(
        top_ranked_df,
        second_ranked_df[['source', 'scan', 'rank2score', 'rank2peptide']],
        how='inner',
        on=['source', 'scan'],
    )
    top_ranked_df = pd.merge(
        top_ranked_df,
        third_ranked_df[['source', 'scan', 'rank3score', 'rank3peptide']],
        how='inner',
        on=['source', 'scan'],
    )

    top_ranked_df['deltaScore'] = (
        top_ranked_df['piscesScore1'] - top_ranked_df['rank2score']
    )
    top_ranked_df['delta3Score'] = (
        top_ranked_df['piscesScore1'] - top_ranked_df['rank3score']
    )

    top_ranked_df.to_csv(f'{config.output_folder}/all_top_candidates.csv', index=False)
