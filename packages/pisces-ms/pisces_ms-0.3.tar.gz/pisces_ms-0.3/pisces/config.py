""" Definition of Config class.
"""
import os
import glob
import shutil
from pathlib import Path

from inspire.config import ALL_CONFIG_KEYS
from inspire.run import run_inspire
import yaml

from pisces.constants import FOLDER_NAMES, CONFIG_FILE_NAMES, TREE_SIZE

ALL_PISCES_CONFIG_KEYS = [
    'additionalConfigs',
    'alleles',
    'canIsoCut',
    'casaConfig',
    'casaModel',
    'casaSingImg',
    'collisionEnergy',
    'contaminantsFolder',
    'convertFiles',
    'dbSearchEngine',
    'deNovoMethod',
    'experimentTitle',
    'expandedProteomeFolder',
    'fraggerPath', 'fraggerMemory', 'fraggerParams',
    'dbSearchResults',
    'deNovoResults',
    'enzyme',
    'exhaustiveResults',
    'genome',
    'maxIntervening',
    'ms1Accuracy',
    'mzAccuracy',
    'mzUnits',
    'nCores',
    'netMHCpan',
    'outputFolder',
    'proteome',
    'pValue',
    'runDbSearch',
    'scansFolder',
    'scansFormat',
    'slurmScript',
    'treeSize',
    'useBindingAffinity',
    'useCase',
    'uniprotSearchFolder',
]

class Config:
    """ Holder for configuration of the SPI-ART pipeline.
    """
    def __init__(self, config_file):
        with open(config_file, 'r', encoding='UTF-8') as stream:
            config_dict = yaml.safe_load(stream)
        for config_key in config_dict:
            if config_key not in ALL_PISCES_CONFIG_KEYS:
                raise ValueError(f'Unrecognised key {config_key} found in config file.')
        self.path = config_file
        self._load_data(config_dict)
        self._clean_file_paths()

    def reload(self):
        """ Function to reload the configuration from the file.
        """
        with open(self.path, 'r', encoding='UTF-8') as stream:
            config_dict = yaml.safe_load(stream)
        for config_key in config_dict:
            if config_key not in ALL_PISCES_CONFIG_KEYS:
                raise ValueError(f'Unrecognised key {config_key} found in config file.')
        self._load_data(config_dict)
        self._clean_file_paths()

    def _clean_file_paths(self):
        """ Function to clean the file paths given to inspire.
        """
        home = str(Path.home())

        if isinstance(self.db_search_results, str):
            self.db_search_results = self.db_search_results.replace('~', home).replace(
                '%USERPROFILE%', home
            )
        elif isinstance(self.db_search_results, list):
            self.db_search_results = [
                x.replace('~', home).replace('%USERPROFILE%', home) for x in self.db_search_results
            ]

        self.scans_folder = self.scans_folder.replace('~', home).replace('%USERPROFILE%', home)
        if self.scans_folder.endswith('/'):
            self.scans_folder = self.scans_folder[:-1]
        self.output_folder = self.output_folder.replace('~', home).replace('%USERPROFILE%', home)
        if self.output_folder.endswith('/'):
            self.output_folder = self.output_folder[:-1]

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        if not os.path.exists(f'{self.output_folder}/img'):
            os.makedirs(f'{self.output_folder}/img')
        if not os.path.exists(f'{self.output_folder}/slurm_logs'):
            os.makedirs(f'{self.output_folder}/slurm_logs')
        for sub_folder in FOLDER_NAMES.values():
            if not os.path.exists(f'{self.output_folder}/{sub_folder}'):
                os.makedirs(f'{self.output_folder}/{sub_folder}')
            if not os.path.exists(f'{self.output_folder}/holdingFolder'):
                os.makedirs(f'{self.output_folder}/holdingFolder')
            if not os.path.exists(f'{self.output_folder}/holdingFolder/candidate_psms'):
                os.makedirs(f'{self.output_folder}/holdingFolder/candidate_psms')
            if not os.path.exists(f'{self.output_folder}/final'):
                os.makedirs(f'{self.output_folder}/final')
            if not os.path.exists(f'{self.output_folder}/details'):
                os.makedirs(f'{self.output_folder}/details')

    def _load_data(self, config_dict):
        self.experiment_title = config_dict['experimentTitle']
        home = str(Path.home())

        db_res = config_dict.get('dbSearchResults')
        if db_res is not None:
            self.db_search_results = []
            for result_group in db_res:
                self.db_search_results.extend(glob.glob(result_group))
        else:
            self.db_search_results = None

        dn_res = config_dict['deNovoResults']
        self.de_novo_results = []
        for result_group in dn_res:
            self.de_novo_results.extend(glob.glob(result_group))

        self.scans_folder = config_dict['scansFolder']
        self.scans_format = config_dict['scansFormat']
        self.output_folder = config_dict['outputFolder']
        self.mz_accuracy = config_dict['mzAccuracy']
        self.mz_units = config_dict['mzUnits']
        self.enzyme = config_dict.get('enzyme')
        self.max_intervening = config_dict.get('maxIntervening', False)
        self.convert_files = config_dict.get('convertFiles', True)
        self.tree_size = config_dict.get('treeSize', TREE_SIZE)
        self.n_cores = config_dict['nCores']
        if 'genome' in config_dict:
            self.genome = config_dict['genome']
            self.proteome = f'{self.output_folder}/six_frame_translated.fasta'
        else:
            self.proteome = config_dict['proteome']
        self.ms1_accuracy = config_dict.get('ms1Accuracy', 5)
        self.expanded_proteome_folder = config_dict.get('expandedProteomeFolder')
        self.use_binding_affinity = config_dict.get('useBindingAffinity')
        self.netmhcpan = config_dict.get('netMHCpan')
        self.alleles = config_dict.get('alleles')
        self.collision_energy = config_dict.get('collisionEnergy')
        self.exhaustive_results = config_dict.get('exhaustiveResults')
        self.use_case = config_dict.get('useCase', 'nonCanonicalDiscovery')
        self.additional_configs = config_dict.get('additionalConfigs', {})
        self.p_val_cut_off = config_dict.get('pValue', 0.85)
        self.slurm_script = config_dict.get('slurmScript')
        self.fragger_memory = config_dict.get('fraggerMemory')
        self.fragger_params = config_dict.get('fraggerParams')
        self.fragger_path = config_dict.get('fraggerPath')
        for setting_key in self.additional_configs:
            assert setting_key in ALL_CONFIG_KEYS
        self.contaminants_folder = config_dict.get('contaminantsFolder')
        self.de_novo_method = config_dict.get('deNovoMethod', 'peaksDeNovo')
        self.can_iso_cut = config_dict.get('canIsoCut', 0.05)
        self.db_search_engine = config_dict.get('dbSearchEngine', 'peaks')
        self.run_db_search = config_dict.get('runDbSearch', False)

        # Casa specific settings
        self.casa_config = config_dict.get(
            'casaConfig', f'{home}/inSPIRE_models/utilities/casa_config.yml'
        )
        self.casa_model = config_dict.get('casaModel', None)
        self.casa_sing_img = config_dict.get('casaSingImg', None)
        self.uniprot_search_folder = config_dict.get('uniprotSearchFolder')

    def run_inspire(self, stratum, pipeline):
        """ Function to run an inspire pipeline for a given stratum.
        """
        config_file_name = CONFIG_FILE_NAMES.get(stratum)
        if config_file_name is None:
            run_inspire(pipeline, f'{self.output_folder}/{stratum}/config.yml')
        else:
            run_inspire(pipeline, f'{self.output_folder}/{config_file_name}')

    def move_pisces_file(self, src, dest):
        """ Function to move files around the piscesOutput folder.
        """
        shutil.move(
            f'{self.output_folder}/{src}',
            f'{self.output_folder}/{dest}'
        )

    def remove_pisces_path(self, file_path):
        """ Function to remove files from the pisces output folder.
        """
        full_path = f'{self.output_folder}/{file_path}'
        if os.path.exists(full_path):
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                raise ValueError(f'{full_path} is not a file or directory')

    def copy_pisces_file(self, src, dest):
        """ Function to move files around the pisces output folder.
        """
        full_src_path = f'{self.output_folder}/{src}'
        full_dest_path = f'{self.output_folder}/{dest}'
        if os.path.exists(full_src_path):
            if os.path.isfile(full_src_path):
                shutil.copyfile(
                    full_src_path, full_dest_path,
                )
            elif os.path.isdir(full_src_path):
                if os.path.exists(full_dest_path):
                    self.remove_pisces_path(dest)
                shutil.copytree(full_src_path, full_dest_path)
            else:
                raise ValueError(f'{full_src_path} is not a file or directory')
