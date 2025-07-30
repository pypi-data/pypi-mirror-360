""" Functions for running inSPIRE.
"""
import os
import subprocess
from time import sleep

from inspire.config import Config
from inspire.retention_time import add_delta_irt
from inspire.utils import modify_sequence_for_skyline, fetch_collision_energy
from inspire.input.casanovo import read_casanovo
from inspire.input.peaks_de_novo import read_peaks_de_novo
from inspire.input.mhcpan import read_mhcpan_output
import pandas as pd
import polars as pl
import yaml

from pisces.constants import CONFIG_FILE_NAMES, FOLDER_NAMES, INSPIRE_PROCESSING_PIPELINES
from pisces.spectral_files import retrieve_rt
from pisces.write_configs import copy_config_file, create_config

BATCH_SIZE = 250_000

def run_canonical_inspire(config):
    """ Function to run all required inSPIRE jobs.

    Parameters
    ----------
    config : pisces.config.Config
        Config object controlling the whol experiment.
    """
    if config.convert_files:
        config.run_inspire('Canonical', 'convert')

    if config.run_db_search:
        if config.db_search_engine != 'msfragger':
            raise ValueError('Run dbSearch is only supported for msfragger at the moment.')
        config.run_inspire('Canonical', 'fragger')
        config.reload()
        create_config(config, 'Canonical')

    if config.db_search_results is not None:
        config.run_inspire('Canonical', 'core')

        all_psms_df = pd.read_csv(
            f'{config.output_folder}/canonicalOutput/final_input.tab',
            sep='\t'
        )
        all_psms_df = all_psms_df[all_psms_df['engineScore'] > 20]

        meta_data = {}
        meta_data['dRtMedian'] = float(all_psms_df['deltaRT'].median())
        if 'mhcpanPrediction' in all_psms_df.columns:
            nine_mer_df = all_psms_df[all_psms_df['peptide'].apply(lambda x : len(x) == 9 + 4)]
            meta_data['mhcpanMedian'] = float(nine_mer_df['mhcpanPrediction'].median())
            meta_data['nuggetsMedian'] = float(nine_mer_df['nuggetsPrediction'].median())

        ce_df = pd.read_csv(
            f'{config.output_folder}/canonicalOutput/collisionEnergyStats.csv'
        )
        ce_df['source'] = ce_df['source'].astype(str)

        meta_data['collisionEnergy'] = int(ce_df['collisionEnergy'].iloc[
            ce_df['spectralAngle'].idxmax()
        ])
        with open(
            f'{config.output_folder}/canonicalOutput/meta_data.yml', 'w', encoding='UTF-8',
        ) as yaml_out:
            yaml.dump(meta_data, yaml_out)
    else:
        if config.de_novo_method == 'casanovo':
            all_dn_results, mods_df = read_casanovo(
                config.de_novo_results, config.scans_folder,
                config.scans_format,
            )
            target_dfs = []
            for source_file in sorted(all_dn_results['source'].unique().to_list()):
                filt_targ_df = all_dn_results.filter(pl.col('source').eq(source_file))
                filt_targ_df = filt_targ_df.filter(
                    pl.col('engineScore').gt(filt_targ_df['engineScore'].quantile(0.9))
                )
                target_dfs.append(filt_targ_df)
            all_dn_results = pl.concat(target_dfs)

            all_dn_results = all_dn_results.filter(
                pl.col('deltaScore').gt(0.9)
            )
        else:
            all_dn_results, mods_df = read_peaks_de_novo(config.de_novo_results)
            target_dfs = []
            for source_file in sorted(all_dn_results['source'].unique().to_list()):
                filt_targ_df = all_dn_results.filter(pl.col('source').eq(source_file))
                target_df = target_df.filter(
                    (target_df['engineScore'] > target_df['engineScore'].quantile(0.9))
                )
                target_dfs.append(filt_targ_df)
            all_dn_results = pl.concat(target_dfs)
        all_dn_results = all_dn_results.sort(by='deltaScore', descending=True)
        all_dn_results = all_dn_results.unique(subset=['source', 'scan'])
        all_dn_results = retrieve_rt(all_dn_results, config.scans_folder)
        all_dn_results.write_csv(f'{config.output_folder}/canonicalOutput/formated_df.csv')
        mods_df.to_csv(f'{config.output_folder}/canonicalOutput/formated_mods.csv', index=False)

        mod_weights = dict(zip(mods_df['Identifier'].tolist(), mods_df['Delta'].tolist()))
        all_dn_results = all_dn_results.with_columns(
            pl.struct(['peptide', 'ptm_seq']).map_elements(
                lambda x : modify_sequence_for_skyline(x, mod_weights),
                skip_nulls=False,
                return_dtype=pl.String,
            ).alias('modifiedSequence')
        )
        all_dn_results.select(
            'source', 'scan', 'peptide', 'modifiedSequence', 'charge', 'retentionTime',
        ).write_csv(f'{config.output_folder}/canonicalOutput/spectral_df.csv')
        config.run_inspire('Canonical', 'spectralAngle')
        prosit_df = pl.read_csv(
            f'{config.output_folder}/canonicalOutput/spectral_df_spectralAngle.csv',
            columns=['source', 'scan', 'peptide', 'iRT'],
            dtypes=[pl.String, pl.Int64, pl.String, pl.Float64],
        )
        all_dn_results = all_dn_results.join(
            prosit_df, on=['source', 'scan', 'peptide'], how='inner',
        )
        rt_dfs = []
        can_config = Config(f'{config.output_folder}/canonical_config.yml')
        for scan_file in sorted(all_dn_results['source'].unique().to_list()):
            filt_dn_df = all_dn_results.filter(pl.col('source').eq(scan_file))
            filt_rt_df = add_delta_irt(filt_dn_df, can_config, scan_file)
            rt_dfs.append(filt_rt_df)
        all_dn_results = pl.concat(rt_dfs)
        meta_data_dict = {
            'dRtMedian': all_dn_results['deltaRT'].median(),
            'collisionEnergy': fetch_collision_energy(
                f'{config.output_folder}/canonicalOutput'
            ),
        }

        if config.use_binding_affinity == 'asFeature':
            all_9_mers_df = all_dn_results.filter(pl.col('sequenceLength') == 9)
            if not os.path.exists(f'{config.output_folder}/canonicalOutput/mhcpan'):
                os.mkdir(f'{config.output_folder}/canonicalOutput/mhcpan')

            all_9_mers_df.select('peptide').write_csv(
                f'{config.output_folder}/canonicalOutput/mhcpan/inputLen9_0.txt',
                include_header=False,
            )
            all_9_mers_df.select('peptide').write_csv(
                f'{config.output_folder}/canonicalOutput/nuggets_input.peps',
                include_header=False,
            )
            config.run_inspire('Canonical', 'predictBinding')

            for idx, allele in enumerate(config.alleles):
                if idx == 0:
                    nugget_pred_df = pl.read_csv(
                        f'{config.output_folder}/canonicalOutput/{allele}_nuggets.csv'
                    )
                    nugget_pred_df = nugget_pred_df.rename({'ic50': f'ic50_{allele}'})
                else:
                    mini_pred_df = pl.read_csv(
                        f'{config.output_folder}/canonicalOutput/{allele}_nuggets.csv'
                    )
                    mini_pred_df = mini_pred_df.rename({'ic50': f'ic50_{allele}'})
                    nugget_pred_df = nugget_pred_df.join(
                        mini_pred_df, how='inner', on='peptide',
                    )
            nugget_pred_df = nugget_pred_df.with_columns(
                pl.min_horizontal(*[f'ic50_{allele}' for allele in config.alleles]).alias(
                    'nuggetsPrediction'
                )
            )
            nugget_pred_df = nugget_pred_df.with_columns(
                pl.col('nuggetsPrediction').log10()
            )
            meta_data_dict['nuggetsMedian'] = nugget_pred_df['nuggetsPrediction'].median()


            mhc_pan_df = read_mhcpan_output(
                f'{config.output_folder}/canonicalOutput/mhcpan', alleles=config.alleles,
            )
            mhc_pan_df = mhc_pan_df.rename({
                'Peptide': 'peptide',
                'Aff(nM)': 'mhcpanPrediction'
            })
            mhc_pan_df = mhc_pan_df.with_columns(
                pl.col('mhcpanPrediction').log10()
            )
            meta_data_dict['mhcpanMedian'] = mhc_pan_df['mhcpanPrediction'].median()

        with open(
            f'{config.output_folder}/canonicalOutput/meta_data.yml', 'w', encoding='UTF-8',
        ) as yaml_out:
            yaml.dump(meta_data_dict, yaml_out)


def run_expanded_inspire(config):
    """ Function to run inSPIRE on de novo PSMs.
    """
    if config.collision_energy is None:
        for stratum in ('De Novo', 'Exhaustive', 'Isobar'):
            config.copy_pisces_file(
                'canonicalOutput/collisionEnergyStats.csv',
                f'{FOLDER_NAMES[stratum]}/collisionEnergyStats.csv',
            )

    # Run inSPIRE on de novo candidates
    if os.path.exists(f'{config.output_folder}/deNovoOutput/formated_df'):
        os.remove(f'{config.output_folder}/deNovoOutput/formated_df')
    config.run_inspire('De Novo', 'format')

    run_denovo_inspire(config)


def run_denovo_inspire(config):
    """ Function to run inSPIRE for the de novo candidates.
    """
    n_dfs = split_de_novo_dfs(config)
    os.system(
        f'rm -rf {config.output_folder}/deNovoOutput/mhcpan/*'
    )
    job_ids = []
    for idx in range(n_dfs):
        if config.slurm_script is not None:
            write_slurm_scipt(config)
            result = subprocess.run(
                ['sbatch', 'slurm_script.sh', f'denovo_{idx}'],
                stdout=subprocess.PIPE,
            )
            job_ids.append(
                result.stdout.decode('utf-8').split('Submitted batch job ')[-1].strip()
            )
        else:
            config.move_pisces_file(
                f'holdingFolder/formated_df_{idx}.csv', 'deNovoOutput/formated_df.csv'
            )
            config.remove_pisces_path('/deNovoOutput/mhcpan')

            for pipeline in INSPIRE_PROCESSING_PIPELINES:
                config.run_inspire('De Novo', pipeline)

            config.move_pisces_file(
                'deNovoOutput/final_input.tab', f'holdingFolder/deNovo_pms_{idx}.tab'
            )

    if config.slurm_script:
        wait_on_slurm_jobs(job_ids)

def wait_on_slurm_jobs(job_ids):
    """ Function to wait for slurm jobs to finish.
    """
    finished_job_ids = []
    while len(finished_job_ids) < len(job_ids):
        sleep(30)
        for job_id in job_ids:
            if job_id not in finished_job_ids:
                result = subprocess.run(
                    ['squeue', '--job', job_id],
                    stdout=subprocess.PIPE,
                )
                job_status = result.stdout.decode('utf-8')
                if job_id not in job_status:
                    finished_job_ids.append(job_id)


def split_de_novo_dfs(config):
    """ Function to split up the de novo candidates for individual processing.
    """
    config.move_pisces_file(
        'deNovoOutput/formated_df.csv', 'holdingFolder/deNovo_df.csv'
    )

    formated_df = pl.read_csv(
        f'{config.output_folder}/holdingFolder/deNovo_df.csv'
    )
    formated_df = formated_df.filter(
        pl.col('sequenceLength') <= 30
    )
    formated_df = formated_df.sort(by=['source', 'peptide'])

    if 'id' in formated_df.columns:
        formated_df = formated_df.drop('id')

    partioned_dfs = formated_df.with_row_count('id').with_columns(
        pl.col('id').map_elements(
        lambda i: int(i//BATCH_SIZE),
        return_dtype=pl.Int64,
    )).partition_by('id')

    n_dfs = len(partioned_dfs)
    for idx, split_df in enumerate(partioned_dfs):
        split_df.write_csv(f'{config.output_folder}/holdingFolder/formated_df_{idx}.csv')

    return n_dfs

def run_inspire_slurm(config, process_name):
    """ Function to allow inSPIRE processing of a subset of all PSMs in an isolated
        process.
    """
    process_type, process_index = process_name.split('_')
    print(process_name, process_index)
    if process_type == 'exhaustive':
        cp_folder = FOLDER_NAMES['Exhaustive']
        config_path = CONFIG_FILE_NAMES['Exhaustive']
        df_in_loc = f'holdingFolder/candidate_psms/combined_{process_index}.csv'
        df_out_loc = f'{process_name}/psms.csv'
        out_path = f'holdingFolder/candidate_psms/final_input_{process_index}.tab'
    elif process_type == 'denovo':
        cp_folder = FOLDER_NAMES['De Novo']
        config_path = CONFIG_FILE_NAMES['De Novo']
        out_path = f'holdingFolder/deNovo_pms_{process_index}.tab'
        df_in_loc = f'holdingFolder/formated_df_{process_index}.csv'
        df_out_loc = f'{process_name}/formated_df.csv'
    elif process_type == 'isobar':
        cp_folder = FOLDER_NAMES['Isobar']
        config_path = CONFIG_FILE_NAMES['Isobar']
        out_path = f'holdingFolder/isobarPsms_processed_{process_index}.tab'
        df_in_loc = f'holdingFolder/isobarPsms{process_index}.csv'
        df_out_loc = f'{process_name}/psms.csv'
    else:
        raise ValueError(f'Unknown process name; {process_type}')

    config.copy_pisces_file(cp_folder, process_name)
    config.copy_pisces_file(df_in_loc, df_out_loc)
    copy_config_file(config_path, process_type, process_index, config.output_folder)

    for pipeline in INSPIRE_PROCESSING_PIPELINES:
        config.run_inspire(process_name, pipeline)

    config.move_pisces_file(f'{process_name}/final_input.tab', out_path)
    config.remove_pisces_path(process_name)


def run_exhaustive_inspire(config, idx):
    """ Function to run inSPIRE on exhaustive candidates.
    """
    exahustive_dir = f'{config.output_folder}/exhaustiveOutput'
    if not os.path.exists(exahustive_dir):
        os.mkdir(exahustive_dir)

    if not os.path.exists(f'{config.output_folder}/holdingFolder/candidate_psms'):
        os.mkdir(f'{config.output_folder}/holdingFolder/candidate_psms/{idx}')


    if config.slurm_script is not None:
        job_ids = []
        write_slurm_scipt(config)
        for file_idx in range(len(os.listdir(
            f'{config.output_folder}/holdingFolder/candidate_psms'
        ))):
            result = subprocess.run(
                ['sbatch', 'slurm_script.sh', f'exhaustive_{file_idx}'],
                stdout=subprocess.PIPE,
                check=False,
            )
            job_ids.append(
                result.stdout.decode('utf-8').split('Submitted batch job ')[-1].strip()
            )
        wait_on_slurm_jobs(job_ids)
    else:
        for file_idx, file in enumerate(sorted(os.listdir(
            f'{config.output_folder}/holdingFolder/candidate_psms'
        ))):
            config.move_pisces_file(
                f'holdingFolder/candidate_psms/{file}',
                'holdingFolder/exhaustivePsms.csv',
            )

            for pipeline in INSPIRE_PROCESSING_PIPELINES:
                config.run_inspire('Exhaustive', pipeline)

            config.move_pisces_file(
                'exhaustiveOutput/final_input.tab',
                f'holdingFolder/candidate_psms/final_input_{file_idx}.tab',
            )
            config.remove_pisces_path('exhaustiveOutput/formated_df.csv')
            config.remove_pisces_path('exhaustiveOutput/mhcpan')


def write_slurm_scipt(config, casa=False, file_name=None):
    """ Function to write a slurm script for running inSPIRE or Casanovo on a cluster.
    """
    with open(config.slurm_script, encoding='UTF-8') as in_file:
        content = in_file.read()
        content = content.replace('CONFIG_N_CORES', str(config.n_cores))
        content = content.replace('CONFIG_LOG_FOLDER', f'{config.output_folder}/slurm_logs')

        if casa:
            casa_model_name = config.casa_model.split('/')[-1]
            casa_model_folder = '/'.join(config.casa_model.split('/')[:-1])
            content += (
                f'apptainer run --bind {config.scans_folder}:/mnt --bind ' +
                f' {casa_model_folder}:/model_mnt --env CASA_MODEL=/model_mnt/{casa_model_name},' +
                f'CASA_CONFIG=/mnt/casa_config.yml,OUT_PATH=/mnt/{file_name}.mztab,' +
                f'SCAN_PATH=/mnt/{file_name}.mgf {config.casa_sing_img} '
            )
        else:
            content += (
                f'\npisces --config_file {config.path} --pipeline inSPIRE_Slurm' +
                ' --process_name $1\n'
            )

    script_name = 'slurm_script.sh'
    if casa:
        script_name = f'{config.output_folder}/casa_slurm_script_{file_name}.sh'

    with open(script_name, mode='w', encoding='UTF-8') as out_file:
        out_file.write(content)
