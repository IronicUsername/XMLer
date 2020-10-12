from datetime import date, datetime
from time import sleep
from typing import Any, Dict, IO, List, Tuple

from click import echo
from schwifty import IBAN
from sepaxml import SepaDD, SepaTransfer
from tqdm import tqdm
from unidecode import unidecode

from xmler.utility import single_csv_row


def create_sepa_xml(input_file: IO[str], output_path: str, config: Dict[str, Any]) -> None:
    """Creates a XML file from CSV data.

    Parameters
    ----------
    input_file: IO[str]
        Path to the CSV data.
    output_path: str
        Path to the output data.
        Default is in the project-root/output.
    config: Dict[str, Any]
        Config.json for SEPA XML generation.
    """
    today_s = str(date.today())
    hit_credit = False
    hit_debit = False

    sepa_credit = SepaTransfer(config, clean=True)
    sepa_debit = SepaDD(config, schema='pain.008.002.02', clean=True)

    echo('Getting Data...')
    for i, payment in enumerate(single_csv_row(input_file)):
        p, p_type = _pack_data(payment)

        if p_type == 'credit':
            hit_credit = True
            sepa_credit.add_payment(p)

        if p_type == 'debit':
            hit_debit = True
            sepa_debit.add_payment(p)

    if hit_credit:
        _generate_output(today_s + '_ueberweisung', sepa_credit.export(), output_path)

    if hit_debit:
        _generate_output(today_s + '_gutschrift', sepa_debit.export(), output_path)


def _generate_output(file_name: str, data: bytes, output_path: str) -> None:
    """Writes a XML file from the extracted CSV data."""
    out_path = output_path + file_name + '.xml'
    echo(f'\nSaving file "{file_name}"" to path "{out_path}"...')

    total_size = len(data)
    block_size = 1024

    with tqdm(total=total_size, position=0, leave=True, bar_format='{desc:<5.5}{percentage:3.0f}%|{bar:50}{r_bar}') as pbar:
        with open(out_path, 'wb') as f:
            for i in (data[i: i + block_size] for i in range(0, len(data), block_size)):
                pbar.update(len(i))
                f.write(i)
                sleep(0.001)

    echo('File saved.\n')
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
        p_type = 'credit'

        res['amount'] = int(payment[3][1:])  # type: ignore
        res['execution_date'] = payment[7]
    else:
        p_type = 'debit'

        res['amount'] = int(payment[3])  # type: ignore
        res['type'] = 'RCUR'
        res['collection_date'] = date.today()  # type: ignore
        res['mandate_id'] = payment[5]
        res['mandate_date'] = payment[6]

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
    umlauts = {ord('Ä'): 'Ae', ord('ä'): 'ae',
               ord('Ü'): 'Ue', ord('ü'): 'ue',
               ord('Ö'): 'Oe', ord('ö'): 'oe',
               ord('ß'): 'ss'}
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
