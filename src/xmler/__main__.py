import sys
from typing import IO, Optional

import click

from xmler.converter import create_payment
from xmler.utils import base_path, handle_output_path


@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('-o', '--output-path', default=base_path() + '/output/', type=click.Path(exists=False), help='Location where files are saved to.')
@click.option('--header/--no-header', default=True, help='Print headers as well. Default is yes. Only applies for csv output.')
def cli(input_file: IO[str], output_path: Optional[str], header: bool) -> None:
    """Script handeler for xml conversion.

    Parameters
    ----------
    input_file: IO[str]
        Path to the input CSV file.
    output_path: Optional[str]
        Path to an exising output directory.
    header: bool
        Wether a CSV file contains the table header or not.
        Default is 'True'.
    """
    if input_file is not None and not input_file.name.endswith('csv'):
        click.echo('`input_file` has to be a CSV file.', file=sys.stderr)
        raise click.Abort()

    output_path = handle_output_path(output_path)

    if header:
        next(input_file)

    create_payment(input_file, output_path)
