import datetime
import json
import os
from typing import Any, Dict, List, Tuple

from sepaxml import SepaDD, SepaTransfer


def create_payment(payment: List[str]) -> Any:
    """Lorem ipsum dolor.

    Parameters
    ----------
    payment: List[str]
        CSV data row.

    Returns
    -------
    sepa: Any:
        Lorem ipsum dolor..
    """
    config = json.load(open(_base_path() + '/data/config.json', 'r'))
    p, p_type = _pack_data(payment)

    if p_type == 'debit':
        sepa = SepaDD(config, schema='pain.008.002.02', clean=True)
    elif p_type == 'credit':
        sepa = SepaTransfer(config, clean=True)

    sepa.add_payment(p)

    return sepa


def _pack_data(payment: List[str]) -> Tuple[Dict[str, Any], str]:
    """Create a payment object that can be handeld by the sepaxml lib.

    Parameters
    ----------
    payment: List[str]
        CSV data row.

    Returns
    -------
    ret : Tuple[Dict[str, Any], str]:
        Contains finished payment object and payment type.
    """
    p_type = ''
    payment = _sanatize_data(payment)
    res = {'name': payment[0],
           'IBAN': payment[1],
           'BIC': payment[2],
           'description': payment[4]}

    # decide if credit or debit
    if int(payment[3]) < 0:
        p_type = 'debit'

        res['amount'] = int(payment[3][1:])  # type: ignore
        res['type'] = 'RCUR'
        res['collection_date'] = datetime.date.today()  # type: ignore
        res['mandate_id'] = payment[7]
        res['mandate_date'] = datetime.date.today()  # type: ignore

    else:
        p_type = 'credit'

        res['amount'] = int(payment[3])  # type: ignore
        res['execution_date'] = datetime.date.today()  # type: ignore

    ret = (res, p_type)
    return ret


def _base_path() -> str:
    """Path to project root."""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def _sanatize_data(data: List[str]) -> List[str]:
    """Remove 'bad stuff' from csv dataset.

    Parameters
    ----------
    data: List[str]
        CSV data row.

    Returns
    -------
    data: List[str]:
        Ready-to-go CSV data row.
    """
    # money amount
    bad_chars = [',', '.']
    data[3] = data[3].translate({ord(x): '' for x in bad_chars})

    # create description
    data[4] = f'{data[4]} {data[5]} {data[6]}'
    data.pop(6)
    data.pop(5)

    return data
