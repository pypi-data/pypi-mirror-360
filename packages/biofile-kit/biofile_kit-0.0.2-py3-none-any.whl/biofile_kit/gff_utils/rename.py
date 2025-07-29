#!/usr/bin/env python
"""
File: rename.py
Description: Rename feature ID.
CreateDate: 2025/7/3
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from io import TextIOWrapper
import click
from pybioinformatic import Gff, dataframe_to_str, Displayer

displayer = Displayer(__file__.split('/')[-1], version='0.1.0')


def main(
    gff_file: TextIOWrapper,
    species_name: str,
    version: str,
    npartitions: int,
    output_file: TextIOWrapper = None
):
    with Gff(gff_file) as gff:
        df = gff.rename(species_name=species_name, version=version, npartitions=npartitions)
        s = dataframe_to_str(df, index=False, header=False)
        for line in s.split('\n'):
            split = line.split('\t')
            if split[-1] != 'NaN':
                attr = f'ID={split[-3]};Name={split[-2]};Parent={split[-1]}'
            else:
                attr = f'ID={split[-3]};Name={split[-2]}'
            split = split[:-3]
            split.append(attr)
            click.echo('\t'.join(split), output_file)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('gff_file', nargs=1, metavar='<gff file|stdin>', type=click.File('r'), required=True)
@click.option('-s', '--species-name', 'species_name',
              metavar='<str>', required=True,
              help='Species name.')
@click.option('-v', '--anno-version', 'anno_version',
              metavar='<str>', default='v1.0', show_default=True,
              help='Annotation version.')
@click.option('-n', '--npartitions', 'npartitions',
              metavar='<int>', type=int, default=4, show_default=True,
              help='The number of partitions to distribute the data into for dask processing.')
@click.option('-o', '--output-file', 'output_file',
              metavar='<file|stdout>', type=click.File('w'),
              help='Output file, stdout by default.')
@click.option('-V', '--version', 'version', help='Show author and version information.',
              is_flag=True, is_eager=True, expose_value=False, callback=displayer.version_info)
def run(gff_file, species_name, anno_version, npartitions, output_file):
    """
    This script provides a standardized feature ID renaming scheme for genome annotation files in GFF format.
    It creates species-specific, chromosome-locating, and structured unique identifiers for different types of
    genomic features in accordance with best practices in bioinformatics, ensuring consistency and traceability of
    IDs throughout the annotation file.\n
    1.genes：<species_name>.<chr_name>Gxxxxxx.<annotation_version>\n
    2.mRNAs: <species_name>.<chr_name>Gxxxxxx.x.<annotation_version>\n
    3.other features: <species_name>.<chr_name>Gxxxxxx.x.<feature_type>.x.<annotation_version>
    """
    main(
        gff_file=gff_file,
        species_name=species_name,
        version=anno_version,
        npartitions=npartitions,
        output_file=output_file
    )


if __name__ == '__main__':
    run()
