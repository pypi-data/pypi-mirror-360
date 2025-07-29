#!/usr/bin/env python
"""
File: gff_tools.py
Description: Gtf file tools.
CreateDate: 2025/7/2
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
import click
from biofile_kit.gtf_utils import gtf2bed, gtf_extract_seq, gtf_sort, __version__
from pybioinformatic import Displayer

displayer = Displayer(__file__.split('/')[-1], version=__version__)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def gtf_tools():
    """Gtf file tools."""
    pass


gtf_tools.add_command(gtf_sort, 'sort')
gtf_tools.add_command(gtf_extract_seq, 'extract_seq')
gtf_tools.add_command(gtf2bed, 'to_bed')


if __name__ == '__main__':
    gtf_tools()
