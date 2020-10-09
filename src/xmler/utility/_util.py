import json
import os
import sys
from typing import Any, Dict, IO, Iterator, List

from click import echo, style
from schema import SchemaError

from xmler.config import CONF_STRUC, CONFIG


def base_path() -> str:
    """Path to project root."""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))


def handle_output_path(out_path: str) -> str:
    """Creates output directory if needed also sanitizes output path string."""
    if not out_path.endswith('/'):
        out_path = out_path + '/'

    if not os.path.exists(os.path.dirname(out_path)):
        echo('Creating directory...')
        os.makedirs(os.path.dirname(out_path))

    return out_path


def init_config():
    cnfg_path = base_path() + '/config.json'
    cnfg = None
    try:
        cnfg = json.load(open(cnfg_path))
        echo(style('Found config.\n', fg='green'))
    except Exception:
        echo(style('No config file found!\n', fg='red')
             + 'Continuing with default config...\n')
        res = CONFIG

    if cnfg is not None and _set_config(cnfg):
        res = cnfg

    return res


def _set_config(conf: Dict[str, Any]) -> Dict[str, Any]:
    """Checks the validity of the given config file.
    Sets default config if

    Parameters
    ----------
    conf: Any
        [description].

    Returns
    -------
    Dict[str, Any]:
        [description].
    """
    if not _validate_config(CONF_STRUC, conf):
        echo('Continue with default config file?')
        answer = input('(y)es/(n)o: ')
        if answer in ['y', 'yes']:
            conf = CONFIG
        elif answer in ['n', 'no']:
            echo(style('Stoping.', fg='red'))
            sys.exit(1)

    return conf


def _validate_config(conf_schema, conf):
    """Check integrity of given conf file."""
    try:
        conf_schema.validate(conf)
        return True
    except SchemaError as e:
        echo(style('Config file is not valid.\n' + str(e), fg='yellow'))
        return False


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
