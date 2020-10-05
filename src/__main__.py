import os
import sys
from typing import Any, Dict, IO, Iterator, Optional

import click
from helper import create_payment

# to do generate sepa xml


def _single_sepa_payment(input_file: IO[str]) -> Iterator[Dict[str, Any]]:
    """Load payments from the input_file, allowing a single json or one json per line."""
    payments = 0
    temp = ''
    for line in input_file:
        temp += line
        try:
            payment = temp
            temp = ''
            payments += 1
            payment = payment[:-1].split(';')
            yield payment
        except Exception:
            pass


@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('-o', '--output-path', type=click.Path(exists=True), help='Location where files are saved to.')
@click.option('--header/--no-header', default=True, help='Print headers as well. Default is yes. Only applies for csv output.')
def cli(input_file: IO[str], output_path: Optional[str], header: bool):
    """this scirpt does stuff.
    """
    if output_path is not None and not os.path.isdir(output_path):
        print('`output_path` has to exist and  be a directory', file=sys.stderr)
        raise click.Abort()

    if header:
        next(input_file)

    for payment in _single_sepa_payment(input_file):
        sepa = create_payment(payment)
        print(sepa.export(validate=True))


cli()
