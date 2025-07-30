""" Functions to write configs for inSPIRE canonical and expanded datasets.
"""
import yaml

from pisces.constants import FOLDER_NAMES, CONFIG_FILE_NAMES

def create_config(config, stratum):
    """ Function to create an inspire config for a given stratum.

    Parameters
    ----------
    config : pisces.config.Config
        Config object controlling the whole experiment.
    stratum : str
        Which group are we writing the config for.

    Returns
    -------
    inspire_config : dict
        Dictionary of the inSPIRE configs.
    """
    inspire_config = {
        'experimentTitle': f'{config.experiment_title} {stratum}',
        'fraggerMemory': config.fragger_memory,
        'fraggerPath': config.fragger_path,
        'fraggerDbSplits': 10,
        'searchResults': config.db_search_results,
        'scansFormat': 'mgf',
        'scansFolder': config.scans_folder,
        'outputFolder': f'{config.output_folder}/{FOLDER_NAMES[stratum]}',
        'ms1Accuracy': config.ms1_accuracy,
        'mzAccuracy': config.mz_accuracy,
        'mzUnits': config.mz_units,
        'rescoreMethod': 'percolatorSeparate',
        'silentExecution': True,
        'deltaMethod': 'ignore',
        'reuseInput': True,
        'nCores': config.n_cores,
        'useBindingAffinity': config.use_binding_affinity,
        'alleles': config.alleles,
        'netMHCpan': config.netmhcpan,
        'proteome': config.proteome,
        'dropUnknownPTMs': False,
        'enzyme': config.enzyme,
        'piscesDnEngine': config.de_novo_method,
    }
    if config.fragger_params is not None:
        inspire_config['fraggerParams'] = config.fragger_params


    if stratum == 'Filtered Proteome':
        inspire_config['proteome'] = f'{config.output_folder}/final_search.fasta'
        inspire_config['inferProteins'] = True
        inspire_config['searchEngine'] = 'msfragger'
        inspire_config['remapToProteome'] = True
        inspire_config['dropUnknownPTMs'] = False
        inspire_config['additionalPsms'] = f'{config.output_folder}/all_remapped_psms.csv'

    if stratum == 'Canonical':
        inspire_config['replaceIL'] = True
        inspire_config['remapToProteome'] = True
        inspire_config['dropUnknown'] = True
        inspire_config['searchEngine'] = config.db_search_engine
        if config.run_db_search:
            inspire_config['fraggerMods'] = 'extended'
        if config.db_search_results is None:
            inspire_config['spectralAngleDfs'] = [
                f'{config.output_folder}/canonicalOutput/spectral_df.csv'
            ]

    if stratum not in ('Canonical', 'Filtered Proteome',):
        inspire_config['rtFitLoc'] = f'{config.output_folder}/canonicalOutput'
        inspire_config['forPisces'] = True
        inspire_config['searchEngine'] = config.de_novo_method

    if stratum == 'De Novo':
        inspire_config['searchResults'] = config.de_novo_results
        inspire_config['spectralAngleDfs'] = [
            f'{config.output_folder}/deNovoOutput/plotData.csv'
        ]

    if stratum == 'Isobar':
        inspire_config['searchResults'] = f'{config.output_folder}/holdingFolder/isobarPsms.csv'
        inspire_config['searchEngine'] = 'psms'

    if stratum == 'Exhaustive':
        inspire_config['searchResults'] = [
            f'{config.output_folder}/holdingFolder/exhaustivePsms.csv',
        ]
        inspire_config['searchEngine'] = 'psms'

    if config.collision_energy is not None:
        inspire_config['collisionEnergy'] = config.collision_energy

    inspire_config.update(config.additional_configs)

    with open(
        f'{config.output_folder}/{CONFIG_FILE_NAMES[stratum]}',
        'w', encoding='UTF-8',
    ) as yaml_out:
        yaml.dump(inspire_config, yaml_out)

def copy_config_file(config_path, process_type, process_index, output_folder):
    """ Copy config file to new location.
    """
    sub_folder = f'{process_type}_{process_index}'
    with open(f'{output_folder}/{config_path}', 'r', encoding='UTF-8') as stream:
        config_dict = yaml.safe_load(stream)

    config_dict['searchResults'] = f'{output_folder}/{sub_folder}/psms.csv'
    config_dict['outputFolder'] = f'{output_folder}/{sub_folder}'

    with open(
        f'{output_folder}/{sub_folder}/config.yml',
        'w', encoding='UTF-8',
    ) as yaml_out:
        yaml.dump(config_dict, yaml_out)

def write_inspire_configs(config):
    """ Function to write config files for running all necessary inSPIRE executions.

    Parameters
    ----------
    config : pisces.config.Config
        Config object controlling the whole experiment.
    """
    create_config(config, 'Canonical')
    create_config(config, 'De Novo')
    create_config(config, 'Isobar')
    create_config(config, 'Exhaustive')
    if config.use_case == 'proteomeAssembly':
        create_config(config, 'Filtered Proteome')
