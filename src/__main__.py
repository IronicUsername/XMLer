import os
import sys
from typing import IO, Iterator, List, Optional

import click
from helper import create_payment

# to do generate sepa xml


def _single_csv_row(input_file: IO[str]) -> Iterator[List[str]]:
    """Load payments from the input_file, allowing a single json or one json per line."""
    payments = 0
    temp = ''
    for line in input_file:
        temp += line
        try:
            payment = temp
            temp = ''
            payments += 1
            res = payment[:-1].split(';')
            yield res
        except Exception:
            pass


@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('-o', '--output-path', type=click.Path(exists=True), help='Location where files are saved to.')
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
    if output_path is not None and not os.path.isdir(output_path):
        click.echo('`output_path` has to exist and  be a directory', file=sys.stderr)
        raise click.Abort()

    if header:
        next(input_file)

    for payment in _single_csv_row(input_file):
        sepa = create_payment(payment)
        print(sepa.export(validate=True))


cli()
