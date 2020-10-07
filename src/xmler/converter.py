from datetime import date, datetime
import json
from typing import Any, Dict, IO, List, Tuple

from click import echo
from schwifty import IBAN
from sepaxml import SepaDD, SepaTransfer
from tqdm import tqdm
from unidecode import unidecode

from .utils import base_path, single_csv_row

CONFIG = json.load(open(base_path() + '/config.json', 'r'))


def create_payment(input_file: IO[str], output_path: str) -> None:
    today_s = str(date.today())
    hit_credit = False
    hit_debit = False

    sepa_credit = SepaTransfer(CONFIG, clean=True)
    sepa_debit = SepaDD(CONFIG, schema='pain.008.002.02', clean=True)

    for payment in single_csv_row(input_file):
        p, p_type = _pack_data(payment)

        if p_type == 'credit':
            hit_credit = True
            sepa_credit.add_payment(p)

        if p_type == 'debit':
            hit_debit = True
            sepa_debit.add_payment(p)

    if hit_credit:
        _generate_output(today_s + '_credit', sepa_credit.export(), output_path)

    if hit_debit:
        _generate_output(today_s + '_debit', sepa_debit.export(), output_path)

    echo('\nDone.')


def _generate_output(file_name: str, data: bytes, output_path: str) -> None:
    out_path = output_path + file_name + '.xml'
    echo(f'\nSaving file "{file_name}"" to path "{out_path}"...')

    total_size = len(data)
    block_size = 1024
    t = tqdm(total=total_size, unit='iB', unit_scale=True)

    # https://stackoverflow.com/questions/35580801/chunking-bytes-not-strings-in-python-2-and-3
    def chunked(size, source):
        for i in range(0, len(source), size):
            yield source[i: i + size]

    with open(out_path, 'wb') as f:
        for i in list(chunked(block_size, data)):
            f.write(i)
            t.update(len(i))

    echo('\nFile saved.\n\n')
    f.close


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
        res['collection_date'] = date.today()  # type: ignore
        res['mandate_id'] = payment[5]
        res['mandate_date'] = payment[6]  # type: ignore
    else:
        p_type = 'credit'

        res['amount'] = int(payment[3])  # type: ignore
        res['execution_date'] = payment[7]  # type: ignore

    ret = (res, p_type)
    return ret


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

    # BIC
    if data[2] == '':
        data[2] = str(IBAN(data[1]).bic)

    # money amount
    if '€' in data[3]:
        data[3] = data[3].strip().translate({ord('€'): ''})
    data[3] = data[3].translate({ord(x): '' for x in [',', '.']})

    # create description
    data[4] = f'{data[4]} {data[5]} {data[6]}'
    data.pop(6)
    data.pop(5)

    # mandate date
    data[6] = datetime.strptime(data[6], '%d.%m.%Y').date() if data[6] else date.today()

    # execution date
    data[7] = datetime.strptime(data[7], '%d.%m.%Y').date() if data[7] else date.today()

    return data
