import os
import sys
from typing import IO, Iterator, List

from click import echo


def handle_output_path(out_path: str) -> str:
    """Creates output directory if needed also sanitizes output path string."""
    if not out_path.endswith('/'):
        out_path = out_path + '/'

    if not os.path.exists(os.path.dirname(out_path)):
        echo('Creating directory...')
        os.makedirs(os.path.dirname(out_path))

    return out_path


def base_path() -> str:
    """Path to project root."""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))


def single_csv_row(input_file: IO[str]) -> Iterator[List[str]]:
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

    if payments == 0:
        echo('Could not load the CSV! Please, ensure, that the file has a CSV format.')
        sys.exit(1)
