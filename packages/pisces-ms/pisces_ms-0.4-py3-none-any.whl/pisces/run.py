""" Main Script from which the whole program runs.
"""
from argparse import ArgumentParser

from pisces.config import Config
from pisces.construct_proteome import construct_proteome
from pisces.create_report import create_report
from pisces.delta_scores import get_delta_scores
from pisces.execute_casa import run_casa
from pisces.fdr_estimation import estimate_spliced_fdr
from pisces.format_exhaustive import process_spisnake_candidates
from pisces.inspire import run_canonical_inspire, run_expanded_inspire, run_inspire_slurm
from pisces.merge_ids import merge_identifications
from pisces.preprocess import preprocess_de_novo_psms
from pisces.quantify import quantify_assignments
from pisces.remap import remap_to_proteome
from pisces.permute import create_doublets
from pisces.translate_genome import translate_genome
from pisces.write_configs import write_inspire_configs
from pisces.contaminants import check_contaminants

PISCES_PIPELINES = [
    'translateGenome',

    'runCasa',
    'writeConfigs',
    'canonical',
    'expanded', 'expanded+',
    'exhaustive',
    'scoreCandidates', 'scoreCandidates+',
    'deltas', 'deltas+',
    'permuteCandidates', 'permuteCandidates+',
    'estimateFDR', 'estimateFDR+',
    'proteomeMap', 'proteomeMap+',
    'quantify',
    'createReport',
    'inSPIRE_Slurm',
    'isobarCanonical',
]

def get_arguments():
    """ Function to collect command line arguments.

    Returns
    -------
    args : argparse.Namespace
        The parsed command line arguments.
    """
    parser = ArgumentParser(description='inSPIRE Pipeline for MS Search Results.')

    parser.add_argument(
        '--config_file',
        default=None,
        help='Config file to be read from.',
        required=False,
    )
    parser.add_argument(
        '--pipeline',
        choices=PISCES_PIPELINES,
        default='all',
        help='Pipeline to run.',
        required=False,
    )
    parser.add_argument(
        '--process_name',
        default=None,
        help='Process name if slurm submit used.',
        required=False,
    )

    return parser.parse_args()

def run_pisces(pipeline=None, config_file=None):
    """ Main function of PISCES pipeline.
    """
    if pipeline is None:
        args = get_arguments()
        pipeline = args.pipeline
        config_file = args.config_file

    config = Config(config_file)

    if pipeline == 'runCasa':# or (pipeline == 'all' and config.de_novo_method == 'casanovo'):
        write_inspire_configs(config)
        run_casa(config)
        config.reload()
        write_inspire_configs(config)

    if pipeline == 'inSPIRE_Slurm':
        run_inspire_slurm(
            config, args.process_name
        )

    if pipeline == 'translateGenome':
        translate_genome(config)

    if pipeline in ('all', 'writeConfigs'):
        write_inspire_configs(config)

    if pipeline in ('all', 'canonical'):
        run_canonical_inspire(config)

    if pipeline in ('all', 'expanded', 'expanded+'):
        run_expanded_inspire(config)

    if pipeline in ('all', 'exhaustive'):
        process_spisnake_candidates(config)

    if pipeline in ('all', 'scoreCandidates', 'expanded+', 'scoreCandidates+'):
        preprocess_de_novo_psms(config)

    if pipeline in ('all', 'deltas', 'deltas+', 'expanded+', 'scoreCandidates+'):
        get_delta_scores(config)

    if pipeline in (
        'all', 'permuteCandidates', 'permuteCandidates+', 'expanded+',
        'deltas+', 'scoreCandidates+',
    ):
        create_doublets(config)

    if pipeline in (
        'all', 'estimateFDR', 'estimateFDR+', 'expanded+',
        'permuteCandidates+', 'deltas+', 'scoreCandidates+',
    ):
        estimate_spliced_fdr(config)

    if config.use_case == 'proteomeAssembly':
        if pipeline in (
            'all', 'proteomeMap', 'proteomeMap+', 'estimateFDR+', 'expanded+',
            'permuteCandidates+', 'deltas+', 'scoreCandidates+',
        ):
            construct_proteome(config)
    else:
        if pipeline in (
            'all', 'proteomeMap', 'proteomeMap+', 'estimateFDR+', 'expanded+',
            'permuteCandidates+', 'deltas+', 'scoreCandidates+',
        ):
            if config.db_search_results is not None:
                remapped_df, cryptic_strata = remap_to_proteome(config)
                if config.contaminants_folder is not None:
                    remapped_df = check_contaminants(config, remapped_df, cryptic_strata)
                remapped_df.write_csv(
                    f'{config.output_folder}/mapped_candidates.csv'
                )

            merge_identifications(config)



    if pipeline == 'quantify':
        quantify_assignments(config)

    if pipeline in (
            'all', 'createReport', 'proteomeMap+', 'estimateFDR+',
            'permuteCandidates+', 'deltas+', 'scoreCandidates+', 'expanded+',
        ):
        create_report(config)

if __name__ == '__main__':
    run_pisces()
