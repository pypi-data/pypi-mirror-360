""" Script for downloading uniprot jar files.
"""
import gzip
import os
from pathlib import Path
import shutil
from urllib.request import urlretrieve

UNIPROT_JAR_DOWNLOAD_URL = (
  'https://proteininformationresource.org/download/peptide_match/downloads/PeptideMatchCMD_1.1.jar'
)
SWISS_PROT_FASTA_URL = (
  'https://ftp.uniprot.org/pub/databases/uniprot/knowledgebase/complete/uniprot_sprot.fasta.gz'
)

def download_swissprot_match():
    """ Function to download the required uniprot jar for pisces search.
    """
    home = str(Path.home())

    if not os.path.isdir(f'{home}/inSPIRE_models'):
        os.mkdir(f'{home}/inSPIRE_models')

    peptide_match_jar_path = f'{home}/inSPIRE_models/PeptideMatchCMD_1.1.jar'

    if not os.path.isfile(peptide_match_jar_path):
        urlretrieve(UNIPROT_JAR_DOWNLOAD_URL, peptide_match_jar_path)
    
    sprot_path = f'{home}/inSPIRE_models/sprot_index'
    swissprot_download_path = f'{home}/inSPIRE_models/uniprot_sprot.fasta.gz'
    swissprot_extract_path = f'{home}/inSPIRE_models/uniprot_sprot.fasta'
    
    if not os.path.isdir(sprot_path):
        urlretrieve(SWISS_PROT_FASTA_URL, swissprot_download_path)

        with gzip.open(swissprot_download_path, 'rb') as f_in:
            with open(swissprot_extract_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.system(
            f'java -jar {peptide_match_jar_path} -a index -d {swissprot_extract_path}' +
            f' -i {sprot_path}'
        )

    return peptide_match_jar_path, sprot_path

if __name__ == '__main__':
    download_pisces_models()
    print("Uniprot JAR file downloaded successfully.")