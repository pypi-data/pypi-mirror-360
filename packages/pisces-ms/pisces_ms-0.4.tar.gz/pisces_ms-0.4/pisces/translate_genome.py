""" Functions to translate a genome into protein sequences.
"""
import multiprocessing as mp

CODON_MAP = {
    'AAA': 'K', 'AAC': 'N', 'AAG': 'K', 'AAT': 'N', 'ACA': 'T', 'ACC': 'T',
    'ACG': 'T', 'ACT': 'T', 'AGA': 'R', 'AGC': 'S', 'AGG': 'R', 'AGT': 'S',
    'ATA': 'I', 'ATC': 'I', 'ATG': 'M', 'ATT': 'I', 'CAA': 'Q', 'CAC': 'H',
    'CAG': 'Q', 'CAT': 'H', 'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
    'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R', 'CTA': 'L', 'CTC': 'L',
    'CTG': 'L', 'CTT': 'L', 'GAA': 'E', 'GAC': 'D', 'GAG': 'E', 'GAT': 'D',
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A', 'GGA': 'G', 'GGC': 'G',
    'GGG': 'G', 'GGT': 'G', 'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
    'TAA': '*', 'TAC': 'Y', 'TAG': '*', 'TAT': 'Y', 'TCA': 'S', 'TCC': 'S',
    'TCG': 'S', 'TCT': 'S', 'TGA': '*', 'TGC': 'C', 'TGG': 'W', 'TGT': 'C',
    'TTA': 'L', 'TTC': 'F', 'TTG': 'L', 'TTT': 'F',
}
REVERSE_CODON_MAP = {
    'TTT': 'K', 'TTG': 'N', 'TTC': 'K', 'TTA': 'N', 'TGT': 'T',
    'TGG': 'T', 'TGC': 'T', 'TGA': 'T', 'TCT': 'R', 'TCG': 'S',
    'TCC': 'R', 'TCA': 'S', 'TAT': 'I', 'TAG': 'I', 'TAC': 'M',
    'TAA': 'I', 'GTT': 'Q', 'GTG': 'H', 'GTC': 'Q', 'GTA': 'H',
    'GGT': 'P', 'GGG': 'P', 'GGC': 'P', 'GGA': 'P', 'GCT': 'R',
    'GCG': 'R', 'GCC': 'R', 'GCA': 'R', 'GAT': 'L', 'GAG': 'L',
    'GAC': 'L', 'GAA': 'L', 'CTT': 'E', 'CTG': 'D', 'CTC': 'E',
    'CTA': 'D', 'CGT': 'A', 'CGG': 'A', 'CGC': 'A', 'CGA': 'A',
    'CCT': 'G', 'CCG': 'G', 'CCC': 'G', 'CCA': 'G', 'CAT': 'V',
    'CAG': 'V', 'CAC': 'V', 'CAA': 'V', 'ATT': '*', 'ATG': 'Y',
    'ATC': '*', 'ATA': 'Y', 'AGT': 'S', 'AGG': 'S', 'AGC': 'S',
    'AGA': 'S', 'ACT': '*', 'ACG': 'C', 'ACC': 'W', 'ACA': 'C',
    'AAT': 'L', 'AAG': 'F', 'AAC': 'L', 'AAA': 'F',
}
TRANSLATION_FRAMES = [
    'forward_1',
    'forward_2',
    'forward_3',
    'reverse_1',
    'reverse_2',
    'reverse_3',
]

def translate(dna_seq, frame):
    """ Function to translate a DNA sequence in a given frame.
    """
    frame_number = int(frame.split('_')[1])
    frame_direction = frame.split('_')[0]
    if frame_direction == 'reverse':
        dna_seq = dna_seq[::-1]
        codon_map = REVERSE_CODON_MAP
    else:
        codon_map = CODON_MAP
    dna_seq = dna_seq[frame_number-1:]
    print('len(dna_seq)',len(dna_seq))
    prot_seq = ''
    for idx in range((len(dna_seq)//3)+1):
        prot_seq += CODON_MAP.get(dna_seq[idx * 3:(idx + 1) * 3], '*')
    return prot_seq


def read_fasta(file_name):
    """ Helper function to read a fasta file.
    """
    seq = ''
    with open(file_name, mode='r') as in_file:
        while line := in_file.readline():
            if not line.startswith('>'):
                seq += line.strip('\n')
    return seq

def process_frame(chromosome_name, chromosome_seq, frame, output_folder):
    replace_chrom = chromosome_name.replace(' ', '-')
    print(f'Translating {replace_chrom} in frame {frame}...')
    prot_seq = translate(chromosome_seq, frame)

    # with open(f'{output_folder}/{replace_chrom}_{frame}.fasta', mode='w') as out_f:
    #     out_f.write(f'>{chromosome_name} | {frame}\n')
    #     # out_write_seq = ''
    #     # while prot_seq:
    #     #     out_write_seq += f'{prot_seq[:60]}\n'
    #     #     prot_seq = prot_seq[60:]
    #     out_f.write(prot_seq)
    #     out_f.write('\n')

    print(f'Translated {replace_chrom} in frame {frame}...')

    return (f'{replace_chrom}_{frame}', prot_seq)

def translate_genome(config):
    genome = {}

    bufsize = 65536
    with open(config.genome) as infile:
        chromosome_name = None
        chromosome_seq = ''
        idx = 0
        while True:
            lines = infile.readlines(bufsize)
            if not lines:
                break
            for line in lines:
                if line.startswith('>'):
                    if chromosome_name is not None:
                        genome[chromosome_name] = chromosome_seq.upper()
                    chromosome_seq = ''
                    chromosome_name = line[1:-1]
                else:
                    chromosome_seq += line[:-1]
                idx += 1

    genome[chromosome_name] = chromosome_seq.upper()
    print('File read in finished')

    func_args = []
    for chromosome_name, chromosome_seq in genome.items():
        print(chromosome_name, len(chromosome_seq))
        for frame in TRANSLATION_FRAMES:
            func_args.append(
                (chromosome_name, chromosome_seq, frame, config.output_folder)
            )

    with mp.get_context('spawn').Pool(processes=36) as pool:
        output_files = pool.starmap(process_frame, func_args)

    with open(f'{config.output_folder}/six_frame_translated.fasta', mode='w') as out_file:
        for name_and_seq in sorted(output_files):
            chrom_frame = name_and_seq[0]
            possible_orfs = name_and_seq[1].split('*')
            for idx, orf in enumerate(possible_orfs):
                if len(orf) > 5:
                    out_file.write(
                        f'>{chrom_frame}_index_{idx}\n{orf}\n'
                    )
