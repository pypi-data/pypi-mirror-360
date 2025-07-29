#!/usr/bin/env python
"""
File: gap_location.py
Description: Gap location.
CreateDate: 2025/5/26
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Union
from io import TextIOWrapper
import click
from pybioinformatic import Fasta, Displayer

displayer = Displayer(__file__.split('/')[-1], version='0.1.0')


def main(asm_file: Union[str, TextIOWrapper],
         output_file: TextIOWrapper = None):
    with Fasta(asm_file) as fa:
        for seq_obj in fa.parse():
            for gap in seq_obj.locate_gap():
                click.echo(gap, output_file)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('asm_file', metavar='<assembly fasta file | stdin>', required=True, nargs=1)
@click.option('-o', '--output-file', 'output_file',
              metavar='<file|stdout>', type=click.File('w'),
              help='Output file, stdout by default.')
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def run(asm_file, output_file):
    """Gap location."""
    main(asm_file, output_file)


if __name__ == '__main__':
    run()
