import datetime
import os
from typing import Any, Dict, List, Optional, Tuple

from unidecode import unidecode


def create_payment(payment: List[str], output_path: Optional[str]) -> Tuple[Dict[str, Any], str]:
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
        res['mandate_id'] = payment[5]
        res['mandate_date'] = datetime.date.today()  # type: ignore

    else:
        p_type = 'credit'

        res['amount'] = int(payment[3])  # type: ignore
        res['execution_date'] = datetime.date.today()  # type: ignore

    ret = (res, p_type)
    return ret


def _generate_output(data: bytes, output_path: str):
    f = open(output_path + 'stuff.xml', 'wb+')
    f.write(data)
    f.close()
    return


def base_path() -> str:
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
    # name
    umlauts = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}
    data[0] = unidecode(data[0].translate(umlauts))

    # money amount
    data[3] = data[3].translate({ord(x): '' for x in [',', '.']})

    # create description
    data[4] = f'{data[4]} {data[5]} {data[6]}'
    data.pop(6)
    data.pop(5)

    return data
