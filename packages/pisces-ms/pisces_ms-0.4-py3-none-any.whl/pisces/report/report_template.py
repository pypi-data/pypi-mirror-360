""" Functions for generating the html report at the end of the inSPIRE
    pipeline.
"""
import os

from inspire.constants import ENDC_TEXT, OKCYAN_TEXT


def safe_fetch(file_path):
    """ Function to check if a file_path exists and return the contents
        if so.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='UTF-8') as file_contents:
            return file_contents.read()
    return ''

def fill_pisces_report_template(config):
    """ Function to create the final html report and open it in the brower.

    Parameters
    ----------
    config : inspire.config.Config
        The Config object for the whole pipeline.
    figures : dict
        A dictionary containing all of the required plots.
    """
    out_path = os.path.abspath(config.output_folder)

    per_stratum_counts = safe_fetch(f'{out_path}/img/per_stratum.svg')
    can_nc_plot = safe_fetch(f'{out_path}/img/can_nc_plot.svg')
    nc_plot = safe_fetch(f'{out_path}/img/nc_plot.svg')
    cryptic_plot = safe_fetch(f'{out_path}/img/cryptic_breakdown.svg')
    logo_plots = safe_fetch(f'{out_path}/img/logo_plots_len_9.svg')
    logo_comp_plots = safe_fetch(f'{out_path}/img/logo_comp_plots.svg')
    fdr_info_plot = safe_fetch(f'{out_path}/img/fdr_information.svg')
    peaks_comp_plot = safe_fetch(f'{out_path}/img/peaks_comparison.svg')
    per_length_plot = safe_fetch(f'{out_path}/img/per_length_recalls.svg')
    per_source_plot = safe_fetch(f'{out_path}/img/per_source_recalls.svg')
    fdr_reanalysis_plot = safe_fetch(f'{out_path}/img/reidentification.svg')
    len_distro_plot = safe_fetch(f'{out_path}/img/length_distros.svg')
    nc_len_distro_plot = safe_fetch(f'{out_path}/img/nc_length_distros.svg')



    html_string = ('''
    <html>
        <head>
            <link 
                rel="stylesheet"
                href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css"
            >
            <style>
                body{
                    font-family: Helvetica;
                    margin:0 100;
                    padding-bottom: 50px;
                    background:whitesmoke;
                }
                h2{
                    color: firebrick;
                    font-family: Helvetica;
                }
                h3{
                    color: firebrick;
                    font-family: Helvetica;
                }
                h2:after
                {
                    content:' ';
                    display: block;
                    border:0.25px solid #696969;
                    position: absolute;
                    width: 60%;
                    margin-top: 2px;
                    left: 20%;
                }
                table {
                    font-family: Helvetica;
                    width: 60%;
                    border: 2px solid #696969;
                }
                th, td {
                    border: 1px solid #696969;
                    padding: 2px;
                }
            </style>
        </head>
        <body>
            <center>
            <h2>inSPIRE PISCES Report for ''' + config.experiment_title + '''</h2>
            </center>
            <h3>
                Raw Files analysed:
            </h3>
            <table style="width:40%">
        ''' + ''.join([
            f'''
                <tr>
                    <td>{source_file}</td>
                </tr>
            ''' for source_file in [
                x[:-4] for x in os.listdir(config.scans_folder) if x.endswith('.mgf')
            ]
        ]) +
        '''
            </table>
            <h3>
                Non-Canonical Peptides Identified:
            </h3>
            <p>
                The figure shows the numbers of non-canonical peptides identified by
                PISCES at different FDR cut offs..
            </p>
            <center>
        ''' + per_stratum_counts +
        '''
            </center>
            <br><br>
            <p>
                The figure shows the fraction of PISCES identifiable peptides that are canonical,
                contaminant, or non-canonical peptides.
            </p>
            <center>
        ''' + can_nc_plot +
        '''
            </center>
            <br><br>
            <p>
                The figure shows the fraction of PISCES non-canonical peptides belonging to each
                stratum.
            </p>
            <center>
        ''' + nc_plot +
        '''
            </center>
            <br><br>
            <p>
                The figure shows the fraction of PISCES cryptic peptides from each cryptic stratum.
            </p>
            <center>
        ''' + cryptic_plot +
        '''
            </center>
            <h3>
                Sequence Motifs
            </h3>
            <p>
                This figure shows the sequence motifs for different strata.
            </p>
            <center>
        ''' + logo_plots +
        '''
                </center>
                <h3>
                    Sequence Comparisons
                </h3>
                <p>
                    The figure shows comparisons of sequence motifs for different strata.
                </p>
                <center>
        ''' + logo_comp_plots +
        '''
                </center>
                <center>
                <h2> Appendix
                </h2>
                </center>
                <p>
                    This section includes more detailed information which may be helpful for
                    quality control.
                </p>
                <h3> Length Distributions </h3>
                <p> This plot shows the length distributions for canonical peptides in
                comparison to non-canonical peptides identified. There is some identification
                bias - PISCES identifies shorter peptides more easily than longer peptides.
                Hence, we show canonical peptide identifiable via standard target decoy and with
                PISCES. The primary comparison is between canonical peptides identifiable with
                PISCES against non-canonical peptides.
                </p>
                <center>
        ''' + len_distro_plot +
        ''' 
                </center>
                <br><br>
                <p> This plot shows the length distributions amonst non-canonical peptide groups.
                </p>
                <center>
        ''' + nc_len_distro_plot +
        '''
                </center>
                <h3>
                    FDR Estimation
                </h3>
                <p>
                    This figure shows the results of reanalysis of spectra which are assigned to
                    canonical peptide sequences via the standard target-decoy method. The first
                    panel is a precision-recall curve which indicates how effectively PISCES
                    recaptures the correct sequence from the spectra reanalysed. The second
                    indicates how accurately PISCES estimates the false discovery rate based on
                    those canonical spectra.
                </p>
                <center>
        ''' + fdr_reanalysis_plot +
        '''
                </center>
                <br><br>
                <p>
                    The compares peaks and inSPIRE performance.
                </p>
                <center>
        ''' + peaks_comp_plot +
        '''
                </center>
                <br><br>
                <p>
                    The compares peaks and inSPIRE performance over the different raw files
                    in the sample.
                </p>
                <center>
        ''' + per_source_plot +
        '''
                </center>
                <br><br>
                <p>
                    The compares peaks and inSPIRE performance over different lengths.
                </p>
                <center>
        ''' + per_length_plot +
        '''
                </center>
                <p>
                    The figure gives information on the adjusted FDR.
                </p>
                <center>
        ''' + fdr_info_plot +
        '''
                </center>
        '''
    )

    output_path = f'{config.output_folder}/pisces-report.html'
    with open(output_path, 'w', encoding='UTF-8') as output_file:
        output_file.write(html_string)

    print(
        OKCYAN_TEXT +
        '\tReport generated.' +
        ENDC_TEXT
    )
