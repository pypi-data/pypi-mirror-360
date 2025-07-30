""" Constants used throughout PISCES.
"""

AMINO_ACIDS = 'ACDEFGHKLMNPQRSTVWY'
TAG_LENGTH = 6
MOD_WEIGHTS = {
    '+16.0': 15.994915,
    '+119.0': 119.004099,
    '+1.0': 0.984016,
    '+42.0': 42.010565,
    '+57.0': 57.021464,
}
TREE_SIZE = 500

FOLDER_NAMES = {
    'Canonical': 'canonicalOutput',
    'De Novo': 'deNovoOutput',
    'Isobar': 'isobarOutput',
    'Exhaustive': 'exhaustiveOutput',
    'Filtered Proteome': 'filteredSearch',
}

CONFIG_FILE_NAMES = {
    'Canonical': 'canonical_config.yml',
    'De Novo': 'de_novo_config.yml',
    'Isobar': 'isobar_config.yml',
    'Exhaustive': 'exhaustive_config.yml',
    'Filtered Proteome': 'filtered_config.yml',
}
DEAMIDATION_DICT = {'D': 'n', 'E': 'q'}

RESIDUE_WEIGHTS_MOD = {
    'A': 71.037114,
    'R': 156.101111,
    'N': 114.042927,
    'D': 115.026943,
    'C': 103.009185 + 57.021464,
    'E': 129.042593,
    'Q': 128.058578,
    'G': 57.021464,
    'H': 137.058912,
    'I': 113.084064,
    'L': 113.084064,
    'K': 128.094963,
    'M': 131.040485,
    'F': 147.068414,
    'P': 97.052764,
    'S': 87.032028,
    'T': 101.047679,
    'W': 186.079313,
    'Y': 163.06332,
    'V': 99.068414,
    'n': 114.042927 + 0.984016,
    'q': 128.058578 + 0.984016,
}
INSPIRE_PROCESSING_PIPELINES = (
    'prepare',
    'predictBinding',
    'predictSpectra',
    'featureGeneration',
    'featureSelection',
)


RESIDUE_WEIGHTS = {
    'A': 71.037114,
    'R': 156.101111,
    'N': 114.042927,
    'D': 115.026943,
    'C': 103.009185,
    'E': 129.042593,
    'Q': 128.058578,
    'G': 57.021464,
    'H': 137.058912,
    'I': 113.084064,
    'L': 113.084064,
    'K': 128.094963,
    'M': 131.040485,
    'F': 147.068414,
    'P': 97.052764,
    'S': 87.032028,
    'T': 101.047679,
    'W': 186.079313,
    'Y': 163.06332,
    'V': 99.068414,
}

H = 1.007825035
O = 15.99491463

N_TERMINUS = H
C_TERMINUS = O + H


EMPTY_SPLICING_RESULTS = {
    'nSplicedProteins': 0,
    'splicedProteins': 'unknown',
    'sr1_Index': '',
    'sr2_Index': '',
    'sr1': '',
    'interveningSeqLengths': '',
    'isForward': '',
}

MODEL_PATH = '{home}/inSPIRE_models/pisces_models/{setting}/{dn_method}/model{model_step}/clf{model_idx}_all.json'


SOURCE_KEY = 'source'
SCAN_KEY = 'scan'
PEPTIDE_KEY = 'peptide'
MOD_SEQ_KEY = 'modifiedSequence'

PROTON = 1.007276466622
ION_OFFSET = {
    'b': N_TERMINUS - H,
    'y': C_TERMINUS + H,
}


MASS_DIFF_CUT = 0.1
