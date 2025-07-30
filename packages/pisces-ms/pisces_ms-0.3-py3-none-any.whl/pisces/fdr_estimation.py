""" Function for providing FDR estimation of top ranked de novo PSMs.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import minimize
import xgboost as xgb

from pisces.constants import MODEL_PATH
from pisces.plot_utils import create_fdr_plots, create_re_id_fig
from pisces.utils import bounded_sigmoid, total_likelihood

FEATURE_SET = [
    'piscesScore1',
    'secondScore',
    'deltaScore',
    'delta3Score',
    'isoDeltaScore',
    'isoDelta2Score',
    'isoDelta3Score',
    'mutated',
]


def get_assigned_canonical_df(output_folder):
    """ Function to get PSMs assigned canonical at 1% FDR.
    """
    final_canonical_df = pd.read_csv(
        f'{output_folder}/canonicalOutput/finalPsmAssignments.csv'
    )
    final_canonical_df['source'] = final_canonical_df['source'].astype(str)

    assigned_canonical_df = final_canonical_df[
        final_canonical_df['postErrProb'] < 0.01
    ]
    assigned_canonical_df = assigned_canonical_df[['source', 'scan', 'peptide']]
    assigned_canonical_df = assigned_canonical_df.rename(
        columns={'peptide': 'correctPeptide'}
    )
    assigned_canonical_df = assigned_canonical_df.drop_duplicates(
        subset=['source', 'scan'], keep=False,
    )
    print(assigned_canonical_df.shape)
    return assigned_canonical_df

def apply_model_2(top_ranked_df, use_binding_affinity, enzyme, dn_method):
    """ Functions to apply model 2.
    """
    clf = xgb.XGBClassifier()
    if enzyme == 'trypsin':
        setting = 'trypsin'
        model_idx = 0
    else:
        setting = 'ip'
        if use_binding_affinity is not None:
            model_idx = 0
        else:
            model_idx = 2

    home = str(Path.home())
    clf.load_model(
        MODEL_PATH.format(
            home=home,
            setting=setting,
            dn_method=dn_method,
            model_step=2,
            model_idx=model_idx,
        )
    )

    top_ranked_df['piscesScore'] = clf.predict_proba(top_ranked_df[FEATURE_SET])[:,1]

    return top_ranked_df

def add_q_values(prob_df, prob_column, q_val_column):
    """ Function to add q-values to identifications based on the peptide/PSM probabilities.
    """
    prob_df = prob_df.sort_values(prob_column, ascending=False).reset_index(drop=True)

    sum_probs = []
    for idx, prob in enumerate(prob_df[prob_column].to_list()):
        pep = 1 - prob
        if idx:
            sum_probs.append((sum_probs[-1] + pep))
        else:
            sum_probs.append(pep)

    q_vals = []
    for idx, prob in enumerate(sum_probs):
        q_vals.append(prob/(idx+1))

    prob_df[q_val_column] = pd.Series(q_vals)
    return prob_df

def calculate_q_values(prob_df, prob_column):
    """ Function to calculate q-values based on individual PSM probabilities.
    """
    prob_df = add_q_values(prob_df, prob_column, 'qValue_PSM')

    peptide_df = prob_df[['peptide', prob_column]].sort_values(
        by=prob_column, ascending=False,
    ).drop_duplicates(subset=['peptide'])
    peptide_df = add_q_values(peptide_df, prob_column, 'qValue_peptide')

    prob_df = pd.merge(
        prob_df, peptide_df[['peptide', 'qValue_peptide']],
        how='inner', on='peptide',
    )

    return prob_df


def estimate_spliced_fdr(config):
    """ Function to provide False discovery rate estimation
    """
    top_ranked_df = pd.read_csv(
        f'{config.output_folder}/double_top_candidates.csv'
    )
    top_ranked_df['source'] = top_ranked_df['source'].astype(str)
    top_ranked_df = top_ranked_df[
        top_ranked_df['peptide'].str.len() > 6
    ]
    top_ranked_df = apply_model_2(
        top_ranked_df, config.use_binding_affinity,
        config.enzyme, config.de_novo_method,
    )

    if config.use_case == 'proteomeAssembly' or config.db_search_results is None:
        top_ranked_df =  calculate_q_values(top_ranked_df, 'piscesScore')
        top_ranked_df = top_ranked_df[
            ['source', 'scan', 'peptide', 'modifiedSequence'] + FEATURE_SET +
            ['piscesScore', 'qValue_PSM', 'qValue_peptide',]
        ].sort_values(by='piscesScore', ascending=False)
    else:
        assigned_canonical_df = get_assigned_canonical_df(config.output_folder)

        labelled_df = pd.merge(
            top_ranked_df,
            assigned_canonical_df,
            how='inner',
            on=['source', 'scan'],
        )
        print(labelled_df.shape)
        labelled_df['correct'] = labelled_df.apply(
            lambda x: 1 if x['peptide'].replace(
                'I', 'L'
            ) == x['correctPeptide'].replace('I', 'L') else 0,
            axis=1,
        )
        print(labelled_df['piscesScore'].mean())
        print(labelled_df['correct'].value_counts())
        labelled_df = labelled_df.sort_values(
            by=['piscesScore', 'peptide'], ascending=[False, True],
        ).reset_index(drop=True)

        labelled_df, top_ranked_df = optimise_model_probabilities(
            labelled_df, top_ranked_df, config.output_folder,
        )

        top_ranked_df = calculate_q_values(top_ranked_df, 'adjustedProbability')
        labelled_df = calculate_q_values(labelled_df, 'adjustedProbability')
        labelled_df.sort_values('qValue_PSM').to_csv(
            f'{config.output_folder}/labelled_df.csv', index=False,
        )
        top_ranked_df = top_ranked_df[
            ['source', 'scan', 'peptide', 'modifiedSequence',] + FEATURE_SET +
            ['piscesScore', 'adjustedProbability', 'qValue_PSM', 'qValue_peptide',]
        ].sort_values(by='adjustedProbability', ascending=False)

        create_re_id_fig(config, labelled_df)

    top_ranked_df.sort_values(by='piscesScore', ascending=False).to_csv(
        f'{config.output_folder}/fdr_est_data.csv', index=False
    )


def optimise_model_probabilities(labelled_df, top_ranked_df, output_folder):
    """ Function to optimise model probabilities based on canonical spectra.
    """
    fit_labelled_df = labelled_df[labelled_df['piscesScore'] > 0.75]
    np.random.seed(seed=197)
    print(fit_labelled_df['piscesScore'].mean())
    print(fit_labelled_df['correct'].mean())
    print(fit_labelled_df['correct'].value_counts())
    optimsation_results = minimize(
        total_likelihood,
        x0=[1.0, 0.5],
        args=(fit_labelled_df[['piscesScore', 'correct']]),
        bounds=((0.0, np.inf), (0, 1)),
    )
    print(optimsation_results)
    if optimsation_results.x[1] > 0.999999999999:
        fit_labelled_df = labelled_df[labelled_df['piscesScore'] > 0.7]
        optimsation_results = minimize(
            total_likelihood,
            x0=[1.0, 0.5],
            args=(fit_labelled_df[['piscesScore', 'correct']]),
            bounds=((0.0, np.inf), (0, 1)),
        )
    top_ranked_df['adjustedProbability'] = top_ranked_df['piscesScore'].apply(
        lambda x : bounded_sigmoid(x, optimsation_results.x[0], optimsation_results.x[1])
    )
    labelled_df['adjustedProbability'] = labelled_df['piscesScore'].apply(
        lambda x : bounded_sigmoid(x, optimsation_results.x[0], optimsation_results.x[1])
    )
    create_fdr_plots(
        labelled_df[labelled_df['piscesScore'] > 0.75], optimsation_results, output_folder
    )

    return labelled_df, top_ranked_df
