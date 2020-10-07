import json
import os
import sys
from time import time
from typing import IO, Iterator, List, Optional

import click
from helper import base_path, create_payment
from sepaxml import SepaDD, SepaTransfer

CONFIG = json.load(open(base_path() + '/config.json', 'r'))


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
@click.option('-o', '--output-path', default=base_path() + '/output/', type=click.Path(exists=True), help='Location where files are saved to.')
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

    if output_path is not None and not os.path.isdir(output_path):
        click.echo('`output_path` has to exist and  be a directory', file=sys.stderr)
        raise click.Abort()

    if header:
        next(input_file)

    sepa_credit = SepaTransfer(CONFIG, clean=True)
    sepa_debit = SepaDD(CONFIG, schema='pain.008.002.02', clean=True)
    f_name_credit = ''
    f_name_debit = ''
    for payment in _single_csv_row(input_file):

        p, p_type = create_payment(payment, output_path)
        if p_type == 'credit':
            f_name_credit = f'{p_type}_{time()}.xml'
            sepa_credit.add_payment(p)
        elif p_type == 'debit':
            f_name_debit = f'{p_type}_{time()}.xml'
            sepa_debit.add_payment(p)

    f_credit = open(output_path + f_name_credit, 'wb')
    f_debit = open(output_path + f_name_debit, 'wb')

    if f_name_credit is not None:
        f_credit.write(sepa_credit.export())
        f_credit.close()
    if f_name_debit is not None:
        f_debit.write(sepa_debit.export())
        f_debit.close()


cli()
