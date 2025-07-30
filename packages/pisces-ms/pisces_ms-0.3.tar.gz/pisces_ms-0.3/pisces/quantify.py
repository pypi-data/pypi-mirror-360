""" Functions for label free quanitification of spliced and non-spliced peptides.
"""
import pandas as pd
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.figure_factory as ff
import scipy

from pisces.plot_utils import clean_plotly_fig


STRATA = [
    'Canonical (PISCES)',
    'Canonical (T/D Only)',
    'Spliced',
    'Spliced/Cryptic',
    'Cryptic',
    'Unknown',
]

COLOURS = [
    'darkorange',
    'goldenrod',
    '#9BBFE5',
    '#8AA53D',
    '#BA69BE',
    '#B9B2C2',
]


def quantify_assignments(config):
    """ Quantify spliced and non-spliced assignments.
    """
    config.run_inspire('De Novo', 'quantify')

    plot_successfully_quantified(config)
    plot_quantification_per_stratum(config)
    # plot_correlation_per_stratum(config)


def get_stratum(pseudo_prot_name):
    """ Get the stratum name from the pseudo protein name
    """
    if pseudo_prot_name.startswith('canonical_pisces_disc'):
        return 'Canonical (PISCES)'
    if pseudo_prot_name.startswith('canonical_td_only'):
        return 'Canonical (T/D Only)'
    if pseudo_prot_name.startswith('spliced'):
        return 'Spliced'
    if pseudo_prot_name.startswith('multimapped'):
        return 'Spliced/Cryptic'
    if pseudo_prot_name.startswith('cryptic'):
        return 'Cryptic'
    return 'Unknown'


def plot_successfully_quantified(config):
    """ Plot distributions of intensities for different strata.
    """
    normed_quant_df = pd.read_csv(
        f'{config.output_folder}/deNovoOutput/quant/normalised_quantification.csv'
    )
    quant_cols = [col for col in normed_quant_df.columns if col.endswith('_norm')]
    normed_quant_df['stratum'] = normed_quant_df['proteins'].apply(get_stratum)
    strata_counts = normed_quant_df['stratum'].value_counts()
    normed_quant_df['meanArea'] = normed_quant_df[quant_cols].mean(axis=1)
    normed_quant_df = normed_quant_df.dropna(subset='meanArea')
    strata_counts_after_dropna = normed_quant_df['stratum'].value_counts()


    fig = go.Figure()
    for idx, stratum in enumerate(STRATA):
        fig.add_trace(go.Bar(
            x=[stratum],
            y=[100*strata_counts_after_dropna[stratum]/strata_counts[stratum]],
            marker_color=COLOURS[idx],
            marker_line_color='black',
            opacity=0.8,
        ))
    fig.update_traces(marker_line_width=0.5)

    fig = clean_plotly_fig(fig)
    fig.update_yaxes(range=[0,100])
    pio.write_image(fig, f'{config.output_folder}/img/quant_success.svg')


def plot_quantification_per_stratum(config):
    """ Plot distributions of intensities for different strata.
    """
    normed_quant_df = pd.read_csv(
        f'{config.output_folder}/deNovoOutput/quant/normalised_quantification.csv'
    )
    normed_quant_df = normed_quant_df[normed_quant_df['peptide'].str.len() == 9]
    quant_cols = [col for col in normed_quant_df.columns if col.endswith('_norm')]
    normed_quant_df['stratum'] = normed_quant_df['proteins'].apply(get_stratum)
    normed_quant_df['meanArea'] = normed_quant_df[quant_cols].mean(axis=1)
    normed_quant_df = normed_quant_df.dropna(subset='meanArea')

    dfs = [normed_quant_df[normed_quant_df['stratum'] == stratum] for stratum in STRATA]

    fig = ff.create_distplot(
        [df['meanArea'] for df in dfs],
        STRATA,
        show_hist=False,
        show_rug=False,
        colors=COLOURS,
    )
    for idx, quant_df in enumerate(dfs):
        fig.add_vline(
            x=quant_df['meanArea'].median(),
            line={'color':COLOURS[idx], 'dash': 'dash', 'width': 1.5},
        )

    fig.update_traces(line_width=1.5)

    fig = clean_plotly_fig(fig)

    fig.update_xaxes(range=[10, 40])
    fig.update_yaxes(range=[0,0.3])

    pio.write_image(fig, f'{config.output_folder}/img/quant_distro.svg')

def plot_correlation_per_stratum(config):
    """ Plot correlation of intensities for different strata.
    """
    normed_quant_df = pd.read_csv(
        f'{config.output_folder}/deNovoOutput/quant/normalised_quantification.csv'
    )
    quant_cols = [col for col in normed_quant_df.columns if col.endswith('_norm')]
    file_list = sorted([
        x for x in normed_quant_df.columns if x.endswith('_norm')
    ])
    normed_quant_df['stratum'] = normed_quant_df['proteins'].apply(get_stratum)
    normed_quant_df['meanArea'] = normed_quant_df[quant_cols].mean(axis=1)
    normed_quant_df = normed_quant_df.dropna(subset=quant_cols)

    dfs = [normed_quant_df[normed_quant_df['stratum'] == stratum] for stratum in STRATA]

    fig = make_subplots(rows=2, cols=3, subplot_titles=STRATA, vertical_spacing=0.14)

    for idx, df in enumerate(dfs):

        correlations = {}
        for source in file_list:
            correlations[source] = []
            for source2 in file_list[::-1]:
                sub_quant_df = df[
                    (df[source].notna()) &
                    (df[source2].notna())
                ]

                correlations[source].append(
                    round(
                        scipy.stats.pearsonr(
                            sub_quant_df[source],
                            sub_quant_df[source2],
                        )[0],
                        2,
                    )
                )


        cor_df = pd.DataFrame(correlations)
        cor_df.index = file_list
        fig.add_trace(
            go.Heatmap(
                z=cor_df.values,
                x=file_list,
                y=file_list[::-1],
                text=cor_df.values,
                texttemplate="%{text}",
                # textfont={"size":3},
                colorscale='RdBu_r',
                # coloraxis_showscale=False,
                zmin=0,zmax=1,
            ), row=(idx//3)+1, col=(idx%3)+1,
        )
    fig.update_layout(
        {
            'coloraxis': {'showscale': False},
            'coloraxis2': {'showscale': False},
            'coloraxis3': {'showscale': False},
            'coloraxis4': {'showscale': False},
            'coloraxis5': {'showscale': False},
            'coloraxis6': {'showscale': False}
        },
    )

    fig.update_layout(
        width=800,
        height=550,
        font_size=8,
        font_family='Helvetica',
        font_color='black',
        margin={'r':25, 'l':25, 't':25, 'b':25},
    )
    pio.write_image(fig, f'{config.output_folder}/img/quant_correlations.svg')
