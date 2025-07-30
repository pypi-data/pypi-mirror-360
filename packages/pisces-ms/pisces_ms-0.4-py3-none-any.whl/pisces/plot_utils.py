""" Functions for plotting.
"""
from copy import deepcopy
from math import ceil
import os

from inspire.input.casanovo import read_casanovo
from inspire.input.peaks_de_novo import read_peaks_de_novo
import logomaker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import polars as pl
from scipy.stats import fisher_exact
# from statsmodels.sandbox.stats.multicomp import multipletests

from pisces.constants import AMINO_ACIDS
from pisces.custom_logo import CustomLogo
from pisces.utils import bounded_sigmoid, total_likelihood

CUT_OFFS = [0.01, 0.02, 0.05, 0.1]

COLOUR_DICT = {
    'spliced': '#9BBFE5',
    'multimapped': '#8AA53D',
    'cryptic': '#BA69BE',
    'contaminants': '#B5AE70',
    'unmapped': '#B9B2C2',
}
AA_COLOUR_SCHEME = {
    'P': 'deeppink',
    'M': 'orange',
    'A': 'orange',
    'V': 'orange',
    'I': 'orange',
    'L': 'orange',
    'F': 'orange',
    'Y': 'orange',
    'W': 'orange',
    'H': 'seagreen',
    'R': 'seagreen',
    'K': 'seagreen',
    'D': 'firebrick',
    'E': 'firebrick',
    'N': 'dodgerblue',
    'Q': 'dodgerblue',
    'S': 'dodgerblue',
    'T': 'dodgerblue',
    'G': 'dodgerblue',
    'C': 'dodgerblue',
    'X': 'black',
}
CRYPTIC_STRATA = [
    'TrEMBL',
    'fiveUTR',
    'threeUTR',
    'CDS_frameshift',
    'lncRNA',
    'intronic',
    'intergenic',
]
DARK_COLOURS = [
    'dodgerblue',
    'orange',
    'yellow',
    'purple',
    'darkgrey',
    'forestgreen',
    'navy',
    'pink',
    'cyan',
    'white',
    'cyan',
    'coral',
    'coral',
]
LIGHT_COLORS = [
    'lightblue',
    'goldenrod',
    'lightyellow',
    'pink',
    'lightgrey',
    'lightgreen',
    'blue',
    'lightcyan',
    'lightcoral',
    'lightcoral',
]
CAN_COLOURS = {
    'canonical (t/d)': '#F4BF91',
    'canonical (PISCES)': '#EC9A56',
}
PLOT_NAMES = {
    'spectralAngle': 'Spectral Angle',
    'spearmanR': 'Spearman Correlation',
    'deltaRT': 'Pred. iRT Error',
    'mhcpanPrediction': 'Predicting BA (log10)',
    'nuggetsPrediction': 'Predicting BA (log10)',
}

def create_logo_plot(amino_acid_data, axis, peptide_length, custom_alphas=None):
    """ Function to clean style on plots.
    """
    logo_plot = CustomLogo(
        amino_acid_data,
        ax=axis,
        font_name='DejaVu Sans',
        color_scheme=AA_COLOUR_SCHEME,
        vpad=.2,
        width=.8,
        # custom_alphas=custom_alphas,
    )
    logo_plot.style_xticks(anchor=1, spacing=1)
    logo_plot.ax.set_xlim([0, peptide_length+1])

    # Hide the right and top spines
    logo_plot.ax.spines.right.set_visible(False)
    logo_plot.ax.spines.top.set_visible(False)

    # Only show ticks on the left and bottom spines
    logo_plot.ax.yaxis.set_ticks_position('left')
    logo_plot.ax.xaxis.set_ticks_position('bottom')
    return logo_plot, axis


def plot_assigned_psms(output_folder):
    """ Function to plot the PSMs.
    """

    scatter_plots = []
    for stratum, colour in COLOUR_DICT.items():
        if os.path.exists(f'{output_folder}/final/{stratum}.csv'):
            strat_df = pd.read_csv(f'{output_folder}/final/{stratum}.csv')
            strat_cuts = [strat_df[
                strat_df['qValue_PSM'] < cut_off
            ]['peptide'].nunique() for cut_off in CUT_OFFS]
            scatter_plots.append(
                go.Scatter(
                    x=CUT_OFFS,
                    y=strat_cuts,
                    name=stratum,
                    line={'color': colour},
                    mode='lines+markers',
                    connectgaps=True,
                )
            )

    fig = go.Figure(data=scatter_plots)
    fig = clean_plotly_fig(fig)
    fig.update_xaxes(range=[0,0.1], title='q-value')
    fig.update_yaxes(title='peptides')
    fig.update_layout(
        width=500,
        height=300,
    )
    pio.write_image(fig, f'{output_folder}/img/per_stratum.svg')



def create_basic_logo_plot(
    data_frame_list, title_list, peptide_length, output_folder, amino_acids=AMINO_ACIDS
):
    """ Function to plot frequency of amino acids 
    """
    _, axes = plt.subplots(1, len(data_frame_list), figsize=(3*len(data_frame_list), 3))
    if len(data_frame_list) == 1:
        axes = [axes]
    for col_idx, strat_df in enumerate(data_frame_list):
        if strat_df is None:
            continue
        strat_df = strat_df.drop_duplicates(subset=['peptide'])
        count_df = get_count_df(strat_df, peptide_length, amino_acids)

        info_df = logomaker.transform_matrix(
            count_df,
            from_type='counts',
            to_type='information',
        )
        info_df.to_csv(f'{output_folder}/logo_plots_len_{peptide_length}.csv', index=False)

        logo_plot, axes[col_idx] = create_logo_plot(
            info_df, axes[col_idx], peptide_length
        )

        logo_plot.ax.set_title(title_list[col_idx])
        logo_plot.ax.set_ylim([0, ceil(info_df.sum(axis=1).max())])


    axes[0].set_ylabel('information (bits)')
    plt.tight_layout()
    plt.savefig(f'{output_folder}/logo_plots_len_{peptide_length}.svg', format='svg')


def create_comparison_logo_plot(
        data_frame_list, title_list, peptide_length, output_folder,
        file_name='logo_comp_plots.svg', amino_acids=AMINO_ACIDS,
        y_lim=None, plot_size=3, x_ticks=None, vline=None, axis='left',
        is_count_df=False,
    ):
    """ Function to compare frequencies of amino acids
    """
    dim_val = len(data_frame_list)-1
    n_plots = (dim_val ** 2 + dim_val)//2
    _, axes = plt.subplots(1, n_plots, figsize=(plot_size*n_plots, plot_size))
    if dim_val == 1:
        axes = [axes]
    plot_idx = 0

    for col_idx, stata_df1 in enumerate(data_frame_list[:-1]):
        for row_idx, strata_df2 in enumerate(data_frame_list[col_idx+1:]):
            if stata_df1 is None or strata_df2 is None:
                continue
            if is_count_df:
                count_df_1 = stata_df1
                count_df_2 = strata_df2
            else:
                count_df_1 = get_count_df(stata_df1, peptide_length, amino_acids)
                count_df_2 = get_count_df(strata_df2, peptide_length, amino_acids)
            if not count_df_1.sum().sum() or not count_df_2.sum().sum():
                continue

            js_div, entropies = jensenshannon(
                count_df_1,
                count_df_2,
                axis=1,
            )

            entropy_df = pd.DataFrame(entropies)
            entropy_df.columns = list(amino_acids)
            entropy_df.index += 1

            entropy_df['jsDivergence'] = js_div
            entropy_df = entropy_df.apply(
                lambda x : scale_to_js_divergence(x, amino_acids), axis=1,
            )
            entropy_df = entropy_df.drop(['jsDivergence'], axis=1)
            entropy_df.to_csv(f'{output_folder}/{file_name.split(".")[0]}.csv', index=False)

            p_val_df = get_fishers_exact_pvals(count_df_1, count_df_2, amino_acids, peptide_length)
            signif_dict = get_significance_dict(p_val_df)

            logo_plot, axes[plot_idx] = create_logo_plot(
                entropy_df, axes[plot_idx], peptide_length, signif_dict
            )

            logo_plot.ax.set_title(f'{title_list[col_idx]} vs. {title_list[col_idx+row_idx+1]}')
            if y_lim is not None:
                logo_plot.ax.set_ylim([-y_lim, y_lim])
            if x_ticks is not None:
                logo_plot.ax.set_xticklabels(x_ticks)
            elif np.abs(js_div).max() >= 0.5:
                logo_plot.ax.set_ylim(
                    [-ceil(np.abs(js_div).max()*5)/5, ceil(np.abs(js_div).max()*5)/5]
                )
            elif np.abs(js_div).max() >= 0.2:
                logo_plot.ax.set_ylim(
                    [-ceil(np.abs(js_div).max()*10)/10, ceil(np.abs(js_div).max()*10)/10]
                )
            else:
                logo_plot.ax.set_ylim(
                    [-ceil(np.abs(js_div).max()*20)/20, ceil(np.abs(js_div).max()*20)/20]
                )
            plot_idx += 1

            if axis == 'right':
                logo_plot.ax.yaxis.tick_right()
                logo_plot.ax.yaxis.set_label_position("right")
                logo_plot.ax.spines[['right']].set_visible(True)
                logo_plot.ax.spines[['left']].set_visible(False)



    axes[0].set_ylabel('JS Divergence')
    if vline is not None:
        plt.axvline(x=vline, ymin=0.125, ymax=0.875, linewidth=0.5, color='black', linestyle='--')

    plt.tight_layout()
    plt.savefig(f'{output_folder}/{file_name}', format='svg')


def get_count_df(strat_df, peptide_length, amino_acids):
    """ Function to get counts of amino acids at each position for peptide of a
        given length.
    """
    aa_counts = np.zeros([peptide_length, len(amino_acids)])
    for _, df_row in strat_df.iterrows():
        for pos_idx, amino_acid in enumerate(df_row['peptide']):
            if amino_acid not in amino_acids:
                continue

            aa_counts[pos_idx, amino_acids.index(amino_acid)] += 1

    count_df = pd.DataFrame(
        aa_counts,
        columns=list(amino_acids)
    )
    count_df.index += 1

    return count_df


def jensenshannon(p, q, base=None, *, axis=0, keepdims=False):
    """ Modified js divergence from scipy.
    """
    p = np.asarray(p)
    q = np.asarray(q)
    p = p / np.sum(p, axis=axis, keepdims=True)
    q = q / np.sum(q, axis=axis, keepdims=True)
    m = (p + q) / 2.0
    relative_entropy_fn = np.vectorize(_element_wise_rel_entropy)
    left = relative_entropy_fn(p, m)
    right = relative_entropy_fn(q, m)

    left_sum = np.sum(left, axis=axis, keepdims=keepdims)
    right_sum = np.sum(right, axis=axis, keepdims=keepdims)
    js = left_sum + right_sum
    if base is not None:
        js /= np.log(base)

    return (js / 2.0), left-right


def _element_wise_rel_entropy(x, y):
    """ Function to calculate entropy per element.
    """
    if x > 0 and y > 0:
        return x*np.log(x/y)
    if x == 0 and y >= 0:
        return 0.0
    return np.inf


def scale_to_js_divergence(df_row, amino_acids):
    """ Function to scale positive and negative entropies to JS divergence.
    """
    sum_neg = 0.0
    sum_pos = 0.0
    for a_a in amino_acids:
        if df_row[a_a] > 0:
            sum_pos += df_row[a_a]
        elif df_row[a_a] < 0:
            sum_neg += abs(df_row[a_a])

    for a_a in amino_acids:
        if df_row[a_a] > 0:
            df_row[a_a] = df_row['jsDivergence']*df_row[a_a]/sum_pos
        elif df_row[a_a] < 0:
            df_row[a_a] = df_row['jsDivergence']*df_row[a_a]/sum_neg
    return df_row


def clean_plotly_fig(fig):
    """ Perform common plotly figure updates to preferred style.
    """
    fig.update_layout(
        # paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        bargap=0.1,
        font_family='Helvetica',
        font_color='black',
        margin={'l':0, 'r':0, 't':20, 'b':0},
        height=300,
        width=500,
    )
    fig.update_xaxes(
        showline=True,
        linewidth=0.5,
        linecolor='black',
        showgrid=False,
        ticks="outside",
        tickwidth=0.5,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=0.5,
        linecolor='black',
        showgrid=False,
        ticks="outside",
        tickwidth=0.5,
    )
    return fig


def get_fishers_exact_pvals(count_df_1, count_df_2, amino_acids, pep_len):
    """ Function to get fishers exact p values.
    """
    p_val_list = []

    sums_1 = count_df_1.sum(axis=1)
    sums_2 = count_df_2.sum(axis=1)

    for a_a in amino_acids:
        for idx in range(1,pep_len+1):
            group_1_aa = count_df_1[a_a].iloc[idx-1]
            group_2_aa = count_df_2[a_a].iloc[idx-1]

            group_1_notaa = sums_1.iloc[idx-1] - group_1_aa
            group_2_notaa = sums_2.iloc[idx-1] - group_2_aa

            fishers_array = np.array([
                [group_1_aa, group_2_aa],
                [group_1_notaa, group_2_notaa],
            ])

            _, pvalue = fisher_exact(fishers_array)
            p_val_list.append({
                'position': idx,
                'residue': a_a,
                'count1': group_1_aa,
                'count2': group_2_aa,
                'count1_false': group_1_notaa,
                'count2_false': group_2_notaa,
                'pvalue': pvalue,
            })

    pvalue_df = pd.DataFrame(p_val_list)
    # pvalue_df['adjusted_pValue'] = multipletests(pvalue_df['pvalue'], method='fdr_bh')[1]
    pvalue_df['significant'] = pvalue_df['pvalue'].apply(lambda x : 1 if x < 0.05 else 0.5)

    return pvalue_df

def get_significance_dict(p_val_df):
    """ Helper function to get out the significantce into a dictionary.
    """
    sig_dict = {}
    for _, df_row in p_val_df.iterrows():
        sig_dict[f'{df_row["residue"]}{df_row["position"]}'] = df_row['significant']
    return sig_dict


def plot_cryptic_breakdown(remapped_df, cryptic_df, output_folder):
    """ Create bar plots of the different cryptic strata.
    """
    total_count = remapped_df['peptide'].nunique()
    remapped_df = remapped_df.reset_index(drop=True)

    nc_df = remapped_df[
        (remapped_df['canonical_nProteins'] == 0) &
        (remapped_df['nContamProteins'] == 0) &
        (remapped_df['nSpecific_ContamsProteins'] == 0)
    ]
    nc_df = nc_df.drop_duplicates(subset=['peptide'])

    nc_df = pd.merge(nc_df, cryptic_df, how='inner', on='peptide')

    nc_df_spliced = nc_df[nc_df['nSplicedProteins'] > 0]
    count_df_spliced = get_cryptic_stratum_counts(nc_df_spliced)

    nc_df_not_spliced = nc_df[nc_df['nSplicedProteins'] == 0]
    count_df_not_spliced = get_cryptic_stratum_counts(nc_df_not_spliced)

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=[
            'Unique to Cryptic Strata', 'Multi-mapped to Spliced',
        ],
    )

    y_lim = ceil(max([
        count_df_not_spliced['totalCount'].max()*100/total_count,
        count_df_spliced['totalCount'].max()*100/total_count,
    ]))
    for row_idx, c_df in enumerate([count_df_not_spliced, count_df_spliced]):
        for idx, df_row in c_df.iterrows():
            fig.add_trace(
                go.Bar(
                    x=[df_row['stratum']],
                    y=[df_row['totalCount']*100/total_count],
                    marker_color=LIGHT_COLORS[idx],
                    marker_line_color='black',
                ),
                row=row_idx+1,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=[df_row['stratum']],
                    y=[df_row['uniqueCount']*100/total_count],
                    marker_color=DARK_COLOURS[idx],
                    marker_line_color='black',
                ),
                row=row_idx+1,
                col=1,
            )


    fig.update_layout(
        barmode='overlay',
    )
    fig = clean_plotly_fig(fig)
    fig.update_yaxes(title='frequency (%)', range=[0, y_lim])

    fig.update_layout(
        height=400,
    )

    pio.write_image(fig, f'{output_folder}/cryptic_breakdown.svg')


def get_cryptic_stratum_counts(nc_df):
    """ Function to get counts for each of the cryptic strata.
    """
    count_data = []
    cryptic_strata = deepcopy(CRYPTIC_STRATA)
    if 'fusion_nProteins' in nc_df.columns:
        cryptic_strata += ['fusion']
    if 'mutation_nProteins' in nc_df.columns:
        cryptic_strata += ['mutation']

    for stratum in cryptic_strata:
        strat_df = nc_df[
            nc_df[f'{stratum}_nProteins'] > 0
        ]
        total_count = strat_df['peptide'].nunique()

        for stratum2 in cryptic_strata:
            if stratum == stratum2:
                continue
            strat_df  = strat_df[
                strat_df[f'{stratum2}_nProteins'] == 0
            ]
        unique_count = strat_df['peptide'].nunique()
        count_data.append({
            'stratum': stratum,
            'uniqueCount': unique_count,
            'totalCount': total_count,
        })

    return pd.DataFrame(count_data)

def split_strata(remapped_df):
    """ Split remapped DataFrame into strata DataFrames.
    """
    can_df = remapped_df[
        (remapped_df['canonical_nProteins'] > 0) &
        (remapped_df['nContamProteins'] == 0)
    ]
    contam_df = remapped_df[
        (remapped_df['nContamProteins'] > 0) |
        (remapped_df['nSpecific_ContamsProteins'] > 0)
    ]
    nc_df = remapped_df[
        (remapped_df['canonical_nProteins'] == 0) &
        (remapped_df['nContamProteins'] == 0) &
        (remapped_df['nSpecific_ContamsProteins'] == 0)
    ]
    return can_df, contam_df, nc_df

def plot_canonical_vs_nc(remapped_df, output_folder=None):
    """ Function to plot frequency of canonical, contaminant, and non-canonical peptides.
    """
    total_count = remapped_df['peptide'].nunique()
    remapped_df = remapped_df.reset_index(drop=True)

    can_df, contam_df, nc_df = split_strata(remapped_df)

    fig1 = go.Figure()
    names = [
        'canonical', 'contaminant', 'non-canonical'
    ]
    colours = [
        '#EC9A56', '#B5AE70', 'pink'
    ]
    for idx, dataset in enumerate([can_df, contam_df, nc_df]):
        fig1.add_trace(
            go.Bar(
                x=[names[idx]],
                y=[100*dataset['peptide'].nunique()/total_count],
                marker_color=colours[idx],
                marker_line_color='black',
                opacity=0.8,
            )
        )
    fig1 = clean_plotly_fig(fig1)
    fig1['layout']['yaxis']['range'] = [0,100]
    fig1['layout']['yaxis']['title'] = 'frequency (%)'

    if output_folder is not None:
        pio.write_image(fig1, f'{output_folder}/can_nc_plot.svg')

    spliced_df, mm_df, cryptic_df, unmapped_df = split_nc_strata(nc_df)
    fig2 = go.Figure()
    names = [
        'spliced', 'multi-mapped', 'cryptic', 'unmapped',
    ]
    colours = [
        '#9BBFE5', '#8AA53D', '#BA69BE', '#B9B2C2',
    ]

    for idx, dataset in enumerate([spliced_df, mm_df, cryptic_df, unmapped_df]):
        fig2.add_trace(
            go.Bar(
                x=[names[idx]],
                y=[100*dataset['peptide'].nunique()/total_count],
                marker_color=colours[idx],
                marker_line_color='black',
                opacity=0.8,
            )
        )
    fig2 = clean_plotly_fig(fig2)
    fig2['layout']['yaxis']['title'] = 'frequency (%)'

    if output_folder is not None:
        pio.write_image(fig2, f'{output_folder}/nc_plot.svg')

    return fig1, fig2


def plot_lengths(remapped_df, td_df, output_folder):
    """ Function to plot peptide lengths for canonical and non-canonical.
    """
    remapped_df = remapped_df.drop_duplicates(subset=['peptide'])

    td_df = td_df.drop_duplicates(subset=['peptide'])
    remapped_df['pepLen'] = remapped_df['peptide'].apply(len)
    td_df['pepLen'] = td_df['peptide'].apply(len)

    nc_df = remapped_df[
        (remapped_df['canonical_nProteins'] == 0) &
        (remapped_df['nContamProteins'] == 0) &
        (remapped_df['nSpecific_ContamsProteins'] == 0)
    ]
    can_pisces_df = remapped_df[remapped_df['canonical_nProteins'] > 0]
    names = ['canonical (target/decoy)', 'canonical (pisces)', 'non-canonical']
    fig = make_subplots(rows=3, cols=1, subplot_titles=names)

    max_val = 0
    colors = ['#F4BF91', '#EC9A56', 'pink']
    for idx, df in enumerate([td_df, can_pisces_df, nc_df]):
        df = df.groupby('pepLen', as_index=False)['peptide'].count()
        df['peptide'] /= df['peptide'].sum()
        df['peptide'] *= 100
        df = df[(df['pepLen'] >= 7) & (df['pepLen'] <= 15)]
        max_val = max([max_val, df['peptide'].max()])
        fig.add_trace(
            go.Bar(
                x=df['pepLen'], y=df['peptide'], marker_color=colors[idx],
                marker_line_color='black', marker_line_width=0.5
            ), row=idx+1, col=1,
        )

    max_val = 20*ceil(max_val/20)

    fig = clean_plotly_fig(fig)
    fig.update_xaxes(range=[6.5, 15.5], dtick=1)
    fig.update_yaxes(range=[0, max_val], title='frequency (%)')
    fig['layout']['xaxis3']['title'] = 'peptide length'
    fig.update_layout(bargap=0, height=600, width=600,)

    pio.write_image(fig, f'{output_folder}/length_distros.svg')


def plot_lengths_nc(remapped_df, output_folder):
    """ Function to plot non-canonical peptide lengths.
    """
    remapped_df = remapped_df.drop_duplicates(subset=['peptide'])

    remapped_df['pepLen'] = remapped_df['peptide'].apply(len)
    nc_df = remapped_df[
        (remapped_df['canonical_nProteins'] == 0) &
        (remapped_df['nContamProteins'] == 0) &
        (remapped_df['nSpecific_ContamsProteins'] == 0)
    ]

    spliced_df, mm_df, cryptic_df, unmapped_df = split_nc_strata(nc_df)
    names = [
        'spliced', 'multi-mapped', 'cryptic', 'unmapped',
    ]
    colours = [
        '#9BBFE5', '#8AA53D', '#BA69BE', '#B9B2C2',
    ]
    fig = make_subplots(rows=4, cols=1, subplot_titles=names)

    max_val = 0
    for idx, df in enumerate([spliced_df, mm_df, cryptic_df, unmapped_df]):
        df = df.groupby('pepLen', as_index=False)['peptide'].count()
        df['peptide'] /= df['peptide'].sum()
        df['peptide'] *= 100
        df = df[(df['pepLen'] >= 7) & (df['pepLen'] <= 15)]
        max_val = max([max_val, df['peptide'].max()])
        fig.add_trace(
            go.Bar(
                x=df['pepLen'], y=df['peptide'], marker_color=colours[idx],
                marker_line_color='black', marker_line_width=0.5
            ), row=idx+1, col=1,
        )

    max_val = 20*ceil(max_val/20)

    fig = clean_plotly_fig(fig)
    fig.update_xaxes(range=[6.5, 15.5], dtick=1)
    fig.update_yaxes(range=[0, max_val], title='frequency (%)')
    fig.update_layout(bargap=0, height=800, width=600,
                      margin={'l':0, 'r':0, 't':20, 'b':0},)
    fig['layout']['xaxis4']['title'] = 'peptide length'

    pio.write_image(fig, f'{output_folder}/nc_length_distros.svg')


def split_nc_strata(nc_df):
    """ Utility function to get dataframes from different strata.
    """
    if 'nCrypticProteins' not in nc_df.columns:
        nc_df['nCrypticProteins'] = 0
    spliced_df = nc_df[
        (nc_df['nSplicedProteins'] > 0) &
        (nc_df['nCrypticProteins'] == 0)
    ]
    mm_df = nc_df[
        (nc_df['nSplicedProteins'] > 0) &
        (nc_df['nCrypticProteins'] > 0)
    ]
    cryptic_df = nc_df[
        (nc_df['nSplicedProteins'] == 0) &
        (nc_df['nCrypticProteins'] > 0)
    ]
    unmapped_df = nc_df[
        (nc_df['nSplicedProteins'] == 0) &
        (nc_df['nCrypticProteins'] == 0)
    ]
    return spliced_df, mm_df, cryptic_df, unmapped_df


def create_re_id_fig(config, labelled_df):
    """ Plot results of spectra identified via canonical target-decoy and
        reanalysed by PISCES.
    """
    cut_offs = np.linspace(
        labelled_df['piscesScore'].min(),
        labelled_df['piscesScore'].max(),
        1000,
    )

    reid_rates = []
    for cut_off in cut_offs:
        cut_df = labelled_df[labelled_df['piscesScore'] >= cut_off]
        reid_rates.append({
            'precision': 100*cut_df['correct'].mean(),
            'recall': 100*cut_df['correct'].sum()/labelled_df.shape[0],
            'q-value': 1 - cut_df['adjustedProbability'].mean(),
            'adjustedProbability': cut_df['adjustedProbability'].min(),
        })
    reid_df = pd.DataFrame(reid_rates)
    reid_df.to_csv(f'{config.output_folder}/img/reid_df.csv', index=False)

    fig = make_subplots(rows=1, cols=2)
    fig.add_trace(
        go.Scatter(
            x=reid_df['recall'],
            y=reid_df['precision'],
            mode='lines',
            line_color='darkgreen',
        ),
        row=1, col=1,
    )
    reid_1fdr_cut = reid_df.iloc[
        (reid_df['adjustedProbability'] - config.p_val_cut_off).abs().argmin()
    ]
    fig.add_trace(
        go.Scatter(
            x=[reid_1fdr_cut['recall']],
            y=[reid_1fdr_cut['precision']],
            mode='markers',
            line_color='darkgreen',
            marker_size=12,
        ),
        row=1, col=1,
    )


    fdr_on_can_spectra = []
    for cut_off in [0.01, 0.02, 0.03, 0.04, 0.05, 0.1]:
        fdr_on_can_spectra.append({
            'Estimated FDR': cut_off,
            'Observed FDR': (
                1 - labelled_df[labelled_df['qValue_PSM'] < cut_off]['correct'].mean()
            ),
        })
    fdr_df = pd.DataFrame(fdr_on_can_spectra)
    fdr_df.to_csv(f'{config.output_folder}/img/fdrs_df.csv', index=False)

    fig.add_trace(
        go.Scatter(
            x=fdr_df['Estimated FDR'],
            y=fdr_df['Observed FDR'],
            mode='lines+markers',
            line_color='darkgreen',
            marker_size=10,
        ),
        row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=fdr_df['Estimated FDR'],
            y=fdr_df['Estimated FDR'],
            mode='lines',
            line_color='black',
            line_dash='dash',
        ),
        row=1, col=2,
    )

    fig = clean_plotly_fig(fig)
    fig.update_layout({
        'xaxis_range': [0, 100],
        'xaxis_title': 'recall',
        'yaxis_range': [0, 100],
        'yaxis_title': 'precision',
        'xaxis2_range': [0, 0.12],
        'yaxis2_title': 'observed FDR',
        'yaxis2_range': [0, 0.12],
        'xaxis2_title': 'estimated FDR',
    })
    fig.add_hline(y=95, x0=0, x1=reid_1fdr_cut['recall']/100, line_dash='dash')
    fig.add_vline(x=reid_1fdr_cut['recall'], y0=0, y1=0.95, line_dash='dash')
    fig.update_layout(
        width=1000,
        height=400,
    )

    pio.write_image(fig, f'{config.output_folder}/img/reidentification.svg')


def create_fdr_plots(labelled_df, optimsation_results, output_folder):
    """ Function to create plots describing FDR.
    """
    fig = make_subplots(
        rows=2,
        cols=2,
        specs=[
           [{"colspan": 2}, None],
            [{}, {}],
        ],
        )

    x_marks = np.linspace(0, 1, 1_000)
    convert_probs = [bounded_sigmoid(
        x_val,  optimsation_results.x[0], optimsation_results.x[1]
    ) for x_val in x_marks]
    fig.add_trace(
        go.Scatter(
            x=x_marks, y=convert_probs, mode='lines', marker_color='darkgreen'
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=x_marks, y=x_marks, mode='lines', marker_color='black',
            line_dash='dash', line_width=0.5,
        ),
        row=1, col=1,
    )
    mini_fig = px.bar(
        x=['True Value', 'Ajusted Estimate', 'Raw Estimate'],
        y=[
            labelled_df['correct'].mean()*100,
            labelled_df['adjustedProbability'].mean()*100,
            labelled_df['piscesScore'].mean()*100,
        ],
        color=['darkgrey', 'darkgreen', 'palegreen',],
        color_discrete_sequence=['darkgrey', 'darkgreen', 'palegreen',],
    )
    mini_fig.update_traces(
        marker_line_color='black',
        marker_line_width=0.5,
    )
    for trace in mini_fig['data']:
        fig.add_trace(
            trace,
            row=2, col=1,
        )

    likelihoods = [
        total_likelihood(optimsation_results.x, labelled_df),
        total_likelihood([1.0, 0.5], labelled_df),
    ]
    mini_fig = px.bar(
        x=['Ajusted Neg. Log Likelihood', 'Raw Neg. Log Likelihood'],
        y=likelihoods,
        color=['darkgreen', 'palegreen',],
        color_discrete_sequence=['darkgreen', 'palegreen',],
    )
    mini_fig.update_traces(
        marker_line_color='black',
        marker_line_width=0.5,
    )
    for trace in mini_fig['data']:
        fig.add_trace(
            trace,
            row=2, col=2,
        )

    fig = clean_plotly_fig(fig)
    fig.update_layout(
        barmode='overlay',
        width=600,
        height=700,
        title_x=0.5,
    )
    fig.update_layout(
        {
            'yaxis_showticklabels': True,
            'xaxis1_range': [0,1],
            'xaxis1_title': 'Raw Probability',
            'yaxis1_title': 'Adjusted Probability',
            'yaxis2_title': 'Mean Correct',
            'yaxis1_range': [0,1],
            'yaxis2_range': [0,100],
            'yaxis3_range': [0,500*(ceil(max(likelihoods)/500))],
            'yaxis3_dtick': 500,
        }
    )

    pio.write_image(fig, f'{output_folder}/img/fdr_information.svg')


def compare_to_baseline(config):
    """ Function to compare PISCES performance to that of PEAKS DB.
    """

    if config.de_novo_method == 'peaksDeNovo':
        dn_df, _ = read_peaks_de_novo(config.de_novo_results)
    else:
        dn_df, _ = read_casanovo(
            config.de_novo_results, config.scans_folder,
            config.scans_format,
        )

    labelled_df = pl.read_csv(f'{config.output_folder}/labelled_df.csv')
    dn_df = dn_df.with_columns(
        pl.lit(1).alias('inDeNovo')
    )
    labelled_df = labelled_df.join(
        dn_df.select(['source', 'scan', 'peptide', 'inDeNovo']).unique(),
        how='left', on=['source', 'scan', 'peptide']
    )
    labelled_df = labelled_df.with_columns(
        pl.col('inDeNovo').fill_null(0)
    )

    dn_df = dn_df.rename({'peptide': 'originalDnPeptide'})
    dn_df = dn_df.sort('engineScore', descending=True)
    dn_df = dn_df.unique(['source', 'scan'])
    labelled_df = labelled_df.join(
        dn_df.select(['source', 'scan', 'originalDnPeptide']),
        how='inner', on=['source', 'scan']
    )
    labelled_df = labelled_df.with_columns(
        pl.struct(['correctPeptide', 'originalDnPeptide']).map_elements(
            lambda df_row : 1 if df_row['correctPeptide'] == df_row['originalDnPeptide'] else 0,
            return_dtype=pl.Int8,
        ).alias('originalDnCorrect'),
        pl.struct(['correctPeptide', 'originalPeptide']).map_elements(
            lambda df_row : 1 if df_row['correctPeptide'] == df_row['originalPeptide'] else 0,
            return_dtype=pl.Int8,
        ).alias('correctBeforeMutation'),
        pl.col('correctPeptide').str.len_chars().alias('pepLen')
    )

    fig = go.Figure()
    for dn_type, dn_val, colour in zip(
        ['Considered', 'Original DN', 'Pisces (no mutation)', 'PISCES'],
        [
            labelled_df['inDeNovo'].mean(),
            labelled_df['originalDnCorrect'].mean(),
            labelled_df['correctBeforeMutation'].mean(),
            labelled_df['correct'].mean(),
        ],
        ['black', 'blue', 'cyan', 'green'],
    ):
        fig.add_trace(go.Bar(
            x=[dn_type], y=[100*dn_val], marker_color=colour,
            marker_line_color='black', marker_line_width=0.5,
        ))

    fig = clean_plotly_fig(fig)
    fig.update_yaxes(range=[0, 100], title='percentage correct',)

    pio.write_image(fig, f'{config.output_folder}/img/peaks_comparison.svg')

    fig = make_subplots(rows=1, cols=2)
    per_length_res = []
    for pep_len in range(labelled_df['pepLen'].min(), min([labelled_df['pepLen'].max()+1, 21])):
        sub_true_df = labelled_df.filter(pl.col('pepLen').eq(pep_len))
        if not sub_true_df.shape[0]:
            per_length_res.append({
                'length': pep_len,
                'count': 0,
                'possibleRecall': None,
                'peaksDnRecall': None,
                'piscesRecall': None,
            })
            continue
        per_length_res.append({
            'length': pep_len,
            'count': 100*sub_true_df.shape[0]/labelled_df.shape[0],
            'possibleRecall': 100*sub_true_df.filter(
                pl.col('inDeNovo') == 1
            ).shape[0]/sub_true_df.shape[0],
            'peaksDnRecall': 100*sub_true_df.filter(
                pl.col('originalDnCorrect') == 1
            ).shape[0]/sub_true_df.shape[0],
            'piscesRecall': 100*sub_true_df.filter(
                pl.col('correct') == 1
            ).shape[0]/sub_true_df.shape[0],
        })
    per_len_df = pd.DataFrame(per_length_res)
    fig.add_trace(
        go.Scatter(
            x=per_len_df['length'], y=per_len_df['possibleRecall'],
            mode='lines+markers', line_color='black'
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=per_len_df['length'], y=per_len_df['peaksDnRecall'],
            mode='lines+markers', line_color='blue'
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=per_len_df['length'], y=per_len_df['piscesRecall'],
            mode='lines+markers', line_color='green'
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(x=per_len_df['length'], y=per_len_df['count'], marker_color='grey'),
        row=1, col=2,
    )
    fig = clean_plotly_fig(fig)
    fig.update_layout(width=800)
    fig.update_yaxes(range=[0,100])
    pio.write_image(fig, f'{config.output_folder}/img/per_length_recalls.svg')

    fig = make_subplots(rows=1, cols=2)
    per_raw_file = []
    for source_file in sorted(labelled_df['source'].unique().to_list()):
        source_l_df = labelled_df.filter(pl.col('source').eq(source_file))
        if not source_l_df.shape[0]:
            per_raw_file.append({
                'source': source_file,
                'count': 0,
                'peaksDnRecall': None,
                'piscesRecall': None,
                'possibleRecall': None,
            })
            continue
        per_raw_file.append({
            'source': source_file,
            'count': 100*source_l_df.shape[0]/labelled_df.shape[0],
            'peaksDnRecall': 100*source_l_df.filter(
                pl.col('originalDnCorrect') == 1
            ).shape[0]/source_l_df.shape[0],
            'piscesRecall': 100*source_l_df.filter(
                pl.col('correct') == 1
            ).shape[0]/source_l_df.shape[0],
            'possibleRecall': 100*source_l_df.filter(
                pl.col('inDeNovo') == 1
            ).shape[0]/source_l_df.shape[0],
        })
    per_source_df = pd.DataFrame(per_raw_file)

    fig.add_trace(
        go.Bar(
            x=per_source_df['source'], y=per_source_df['peaksDnRecall'],
            marker_color='blue', marker_line_color='black'
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(
            x=per_source_df['source'], y=per_source_df['piscesRecall'],
            marker_color='green', marker_line_color='black'
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(
            x=per_source_df['source'], y=per_source_df['possibleRecall'],
            marker_color='darkgrey', marker_line_color='black'
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Bar(x=per_source_df['source'], y=per_source_df['count'], marker_color='grey'),
        row=1, col=2,
    )
    fig = clean_plotly_fig(fig)
    fig.update_layout(width=800)
    fig.update_yaxes(range=[0,100])
    pio.write_image(fig, f'{config.output_folder}/img/per_source_recalls.svg')


def plot_qc_figs(config):
    """ Function to plot the quality of noncanonical PSMs.
    """
    config.run_inspire('De Novo', 'spectralAngle')
    config.move_pisces_file(
        'deNovoOutput/plotData_spectralAngle.csv',
        'nonCanonicalMetrics.csv'
    )
    qc_df = pd.read_csv(f'{config.output_folder}/nonCanonicalMetrics.csv')
    if config.use_binding_affinity is not None:
        qc_df['mhcpanPrediction'] = qc_df['mhcpanPrediction'].apply(np.log10)
        qc_df['nuggetsPrediction'] = qc_df['nuggetsPrediction'].apply(np.log10)

    can_df = pd.read_csv(f'{config.output_folder}/canonicalOutput/finalPsmAssignments.csv')
    can_df = can_df[can_df['qValue'] < 0.01]
    pisces_df = pd.read_csv(f'{config.output_folder}/filtered_mapped.csv')
    pisces_df = pisces_df[pisces_df['adjustedProbability'] > config.p_val_cut_off]
    can_df = pd.merge(
        can_df, pisces_df[['peptide']].drop_duplicates(),
        how='left', on='peptide', indicator=True,
    )

    can_df['Context'] = can_df['_merge'].apply(
        lambda x : 'canonical (t/d)' if x == 'left_only' else 'canonical (PISCES)'
    )
    ba_cols = [col for col in can_df.columns if col.endswith('BindingAffinity')]

    plot_features = ['spectralAngle', 'spearmanR', 'deltaRT']
    if config.use_binding_affinity is not None:
        can_df['mhcpanPrediction'] = can_df[ba_cols].apply(
            lambda df_row : np.log10(np.min([df_row[col] for col in ba_cols])), axis=1,
        )
        plot_features.append('mhcpanPrediction')
    for feature in plot_features:
        fig = go.Figure()
        for stratum in ['canonical (t/d)', 'canonical (PISCES)']:
            s_df = can_df[can_df['Context'] == stratum]
            fig.add_trace(
                go.Violin(
                    x=s_df['Context'],
                    y=s_df[feature],
                    points=False,
                    line_color='black',
                    line_width=0.5,
                    fillcolor=CAN_COLOURS[stratum],
                    meanline_visible=True,
                )
            )
        for stratum in ['spliced', 'multimapped', 'cryptic', 'unmapped', 'contaminants']:
            s_df = qc_df[qc_df['Context'] == stratum]
            if feature in ('mhcpanPrediction', 'nuggetsPrediction'):
                s_df = s_df[s_df['sequenceLength'] > 7]
            fig.add_trace(
                go.Violin(
                    x=s_df['Context'],
                    y=s_df[feature],
                    points=False,
                    line_color='black',
                    line_width=0.5,
                    fillcolor=COLOUR_DICT[stratum],
                    meanline_visible=True,
                )
            )
            fig.update_yaxes(title=PLOT_NAMES[feature])
            if feature in ('spectralAngle', 'spearmanR'):
                fig.update_yaxes(range=[0,1])
            elif feature in ('mhcpanPrediction', 'nuggetsPrediction'):
                fig.update_yaxes(range=[0,6])
            else:
                fig.update_yaxes(range=[0,50])

        fig = clean_plotly_fig(fig)
        pio.write_image(fig, f'{config.output_folder}/img/{feature}_distributions.svg')
