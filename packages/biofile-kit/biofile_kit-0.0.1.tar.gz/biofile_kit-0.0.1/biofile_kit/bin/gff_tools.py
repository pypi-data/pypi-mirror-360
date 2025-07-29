#!/usr/bin/env python
"""
File: gff_tools.py
Description: Gff file tools.
CreateDate: 2025/7/2
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
import click
from biofile_kit.gff_utils import get_feature_density, gff2bed, gff2gtf, gff_extract_seq, gff_sort, rename, __version__
from pybioinformatic import Displayer

displayer = Displayer(__file__.split('/')[-1], version=__version__)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def gff_tools():
    """Gff file tools."""
    pass


gff_tools.add_command(get_feature_density, 'get_feature_density')
gff_tools.add_command(gff2bed, 'to_bed')
gff_tools.add_command(gff2gtf, 'to_gtf')
gff_tools.add_command(gff_extract_seq, 'extract_seq')
gff_tools.add_command(gff_sort, 'sort')
gff_tools.add_command(rename, 'rename')


if __name__ == '__main__':
    gff_tools()
