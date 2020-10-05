import datetime
import json
import os
import re
from typing import Any, Dict, List

import chardet
from sepaxml import SepaDD, SepaTransfer


def create_payment(payment: Dict[str, Any]):
    sepa = ''
    config = json.load(open(_base_path() + '/data/config.json', 'r'))
    payment, p_type = _pack_data(payment)

    if p_type == 'debit':
        sepa = SepaDD(config, schema='pain.008.002.02', clean=True)
    elif p_type == 'credit':
        sepa = SepaTransfer(config, clean=True)

    sepa.add_payment(payment)

    return sepa


def _pack_data(payment: List[str]) -> Dict[str, Any]:
    p_type = ''
    payment = _sanatize_data(payment)
    res = {'name': payment[0],
           'IBAN': payment[1],
           'BIC': payment[2],
           'description': payment[4]}

    # decide if credit or debit
    if payment[3] < 0:
        p_type = 'debit'

        res['amount'] = int(str(payment[3])[1:])
        res['type'] = 'RCUR'
        res['collection_date'] = datetime.date.today()
        res['mandate_id'] = payment[7]
        res['mandate_date'] = datetime.date.today()

    else:
        p_type = 'credit'

        res['amount'] = payment[3]
        res['execution_date'] = datetime.date.today()

    return res, p_type


def _base_path() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def _get_encoding(file_path: str) -> str:
    f = chardet.detect(open(file_path, 'rb').read())
    res = f['encoding'] if f['confidence'] >= 0.5 else 'utf-8'

    return res


def _sanatize_data(data: List[str]) -> List[str]:
    # money amount
    data[3] = ''.join(data[3].split(','))
    data[3] = int(''.join(data[3].split('.')))

    # mandate ID
    data[7] = int(re.search(r'\d+', data[7]).group())

    # create description
    data[4] = f'{data[4]} {data[5]} {data[6]}'
    data.pop(6)
    data.pop(5)

    return data
