import os
from typing import IO, Iterator, List


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
