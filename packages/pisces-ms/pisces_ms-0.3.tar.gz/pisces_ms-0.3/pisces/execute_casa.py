""" Module to run casanovo on all available scan_files.
"""
import os
import subprocess

from pisces.inspire import wait_on_slurm_jobs, write_slurm_scipt

def run_casa(config):
    """ Function to run casanovo on all available scan_files.
    """
    config.run_inspire('Canonical', 'convert')
    scan_files = [x for x in os.listdir(config.scans_folder) if x.endswith('.mgf')]

    with open(
        config.casa_config,
        mode='r',
        encoding='UTF-8',
    ) as casa_config:
        casa_config = casa_config.read().format(
            precursor_tolerance=f'{config.ms1_accuracy}',
        )
    with open(
        f'{config.scans_folder}/casa_config.yml',
        mode='w',
        encoding='UTF-8',
    ) as config_file:
        config_file.write(casa_config)


    if config.slurm_script is not None:
        job_ids = []
        for file_name in scan_files:
            stripped_file_name = file_name.split('.')[0]
            write_slurm_scipt(config, casa=True, file_name=stripped_file_name)
            result = subprocess.run(
                ['sbatch', f'{config.output_folder}/casa_slurm_script_{stripped_file_name}.sh',],
                stdout=subprocess.PIPE, check=False,
            )
            job_ids.append(
                result.stdout.decode('utf-8').split('Submitted batch job ')[-1].strip()
            )
        wait_on_slurm_jobs(job_ids)
    else:
        for scan_file in scan_files:
            sf_no_suffix = scan_file.split('.')[-2]
            os.system(
                '/bin/bash -c "source ~/anaconda3/etc/profile.d/conda.sh && ' +
                'conda activate casanovo_env && ' +
                'conda run -n casanovo_env casanovo sequence --config casa_config.yml ' +
                '--model casanovo_nontryptic.ckpt ' +
                f'-o {config.scans_folder}/{sf_no_suffix}.mztab ' +
                f' {config.scans_folder}/{scan_file}"'
            )
