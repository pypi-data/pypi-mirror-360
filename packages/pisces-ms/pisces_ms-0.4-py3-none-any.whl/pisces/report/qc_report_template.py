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

def fill_pisces_qc_report_template(config):
    """ Function to create the final html report and open it in the brower.

    Parameters
    ----------
    config : inspire.config.Config
        The Config object for the whole pipeline.
    figures : dict
        A dictionary containing all of the required plots.
    """
    out_path = os.path.abspath(config.output_folder)

    spectral_angle_plot = safe_fetch(f'{out_path}/img/spectralAngle_distributions.svg')
    spearman_plot = safe_fetch(f'{out_path}/img/spearmanR_distributions.svg')
    delta_rt_plot = safe_fetch(f'{out_path}/img/deltaRT_distributions.svg')
    ba_plot = safe_fetch(f'{out_path}/img/mhcpanPrediction_distributions.svg')
    fdr_info_plot = safe_fetch(f'{out_path}/img/fdr_information.svg')
    peaks_comp_plot = safe_fetch(f'{out_path}/img/peaks_comparison.svg')
    per_length_plot = safe_fetch(f'{out_path}/img/per_length_recalls.svg')
    per_source_plot = safe_fetch(f'{out_path}/img/per_source_recalls.svg')
    fdr_reanalysis_plot = safe_fetch(f'{out_path}/img/reidentification.svg')

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
            <h2>inSPIRE PISCES QC Report for ''' + config.experiment_title + '''</h2>
            </center>
            <p>
                This report describes the quality of PSMs assigned via PISCES and provides
                MS2 comparison plots for non-canonical PSMs identified. It is important to
                check these metrics to ensure the quality of PISCES assignments in terms of
                precision.
            </p>
            <p>
                We also provide metrics measuring PISCES performance in terms of recall
                based on PSMs which were identified via the target-decoy method. It is
                important to check these metrics to ensure that you are maximising your
                peptide yield with PISCES.
            </p>
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
                Quality metrics on identified PSMs
            </h3>
            <p>
                This figure shows distribution of spectral angles calculated by comparing
                experimental spectra to Prosit predicted spectra. Distributions for non-canonical
                strata should be similar to canonical PSMs which are PISCES discoverable
                and superior to canonical PSMs which are discoverable only via a standard
                target decoy approach.
            </p>
            <center>
        ''' + spectral_angle_plot +
        '''
            </center>
            <br><br>
            <p>
                This figure shows distribution of spearman correlations calculated by comparing
                experimental spectra to Prosit predicted spectra. Distributions for non-canonical
                strata should be similar to canonical PSMs which are PISCES discoverable
                and superior to canonical PSMs which are discoverable only via a standard
                target decoy approach.
            </p>
            <center>
        ''' + spearman_plot +
        '''
            </center>
            <br><br>
            <p>
                This figure shows distribution of errors between Prosit predicted indexed
                retention time (iRT) and experimentally observed retention times. Distributions
                for non-canonical strata should be similar to canonical PSMs which are PISCES
                discoverable and superior to canonical PSMs which are discoverable only via a
                standard target decoy approach.
            </p>
            <center>
        ''' + delta_rt_plot +
        '''
            </center>
        '''
    )
    if ba_plot:
        html_string += (
        '''
            <br><br>
            <p>
                This figure shows distribution of netMHCpan predicted binding affinities.
                Distributions for most non-canonical strata should be similar to canonical peptides
                which are PISCES discoverable and superior to canonical peptides which are
                discoverable only via a standard target decoy approach. The exception may be
                contaminant peptides which are not necessarily binders to MHC-I molecules.
            </p>
            <center>
        ''' + ba_plot +
        '''
            </center>
        '''
        )
    html_string += (
        '''
            <h3>
                MS2 Spectral Plots:
            </h3>
            <p>
                These are the MS2 spectra based on which non-canonical peptides were assigned.
                Inspection of the spectra can be informative and increase your confidence in
                peptides identified.
            </p>
            <embed src="
        ''' + f'{config.output_folder}/nonCanonicalPlots.pdf" width=1200 height=2000>' +
        '''
                <h3>
                    FDR Estimation
                </h3>
                <p>
                    This figure shows the results of reanalysis of spectra which are assigned to
                    canonical peptide sequences via the standard target-decoy method. The first
                    panel is a precision-recall curve which indicates how effectively PISCES
                    recaptures the correct sequence from the spectra reanalysed. The second
                    indicates how accurately PISCES estimates the false discovery rate based
                    on those canonical spectra.
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

    output_path = f'{config.output_folder}/pisces-qc-report.html'
    with open(output_path, 'w', encoding='UTF-8') as output_file:
        output_file.write(html_string)

    print(
        OKCYAN_TEXT +
        '\tReport generated.' +
        ENDC_TEXT
    )
