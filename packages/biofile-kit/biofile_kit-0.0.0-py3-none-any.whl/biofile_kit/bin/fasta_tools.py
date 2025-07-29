#!/usr/bin/env python
"""
File: gff_tools.py
Description: Fasta file tools.
CreateDate: 2025/7/2
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
import click
from biofile_kit.fasta_utils import (
    fa2tab,
    format_fasta,
    gap_location,
    generate_random_nucl,
    get_longest_seq_for_gene,
    get_reverse_complementary_seq,
    get_seq_len,
    id_index_seq,
    motif_finder,
    ORF_finder,
    seq_rename,
    SSR_finder,
    __version__
)
from pybioinformatic import Displayer

displayer = Displayer(__file__.split('/')[-1], version=__version__)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def fasta_tools():
    """Fasta file tools."""
    pass


fasta_tools.add_command(fa2tab, 'fa2tab')
fasta_tools.add_command(format_fasta, 'format_fasta')
fasta_tools.add_command(gap_location, 'gap_location')
fasta_tools.add_command(generate_random_nucl, 'random_nucl')
fasta_tools.add_command(get_longest_seq_for_gene, 'get_longest_seq_for_gene')
fasta_tools.add_command(get_reverse_complementary_seq, 'get_reverse_complementary_seq')
fasta_tools.add_command(get_seq_len, 'get_seq_len')
fasta_tools.add_command(id_index_seq, 'id_index_seq')
fasta_tools.add_command(motif_finder, 'motif_finder')
fasta_tools.add_command(ORF_finder, 'ORF_finder')
fasta_tools.add_command(seq_rename, 'seq_rename')
fasta_tools.add_command(SSR_finder, 'SSR_finder')


if __name__ == '__main__':
    fasta_tools()
