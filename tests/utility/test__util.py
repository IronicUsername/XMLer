import os
import pathlib
import tempfile

import pytest

from xmler.utility._util import _set_config, handle_output_path, single_csv_row


@pytest.mark.parametrize('data,solution', [
    pytest.param({'name': 'Cooler Mann',
                  'BIC': 'PBNKDEFFXXX',
                  'IBAN': 'DE85370100500123456503',
                  'batch': True,
                  'creditor_id': 'DE26ZZZ00000000000',
                  'currency': 'EUR'},
                 {'name': 'Cooler Mann',
                  'BIC': 'PBNKDEFFXXX',
                  'IBAN': 'DE85370100500123456503',
                  'batch': True,
                  'creditor_id': 'DE26ZZZ00000000000',
                  'currency': 'EUR'},
                 id='valid config'),
    pytest.param({'name': 'Cooler Mann',
                  'BIC': 'PBNKDEFFXXX',
                  'IBAN': 'DE85370100500123456503',
                  'batch': 'True',
                  'creditor_id': 'DE26ZZZ00000000000',
                  'currency': 'EUR'},
                 {'name': 'Test von Testenstein',
                  'IBAN': 'NL50BANK1234567890',
                  'BIC': 'BANKNL2A',
                  'batch': True,
                  'creditor_id': 'DE26ZZZ00000000000',
                  'currency': 'EUR'},
                 id='invalid config #1 ("batch" has wrong type)'),
    pytest.param({'name': 'Cooler Mann',
                  'BIC': 'PBNKDEFFXXX',
                  'IBAN': 'DE85370100500123456503',
                  'batch': True,
                  'currency': 'EUR'},
                 {'name': 'Test von Testenstein',
                  'IBAN': 'NL50BANK1234567890',
                  'BIC': 'BANKNL2A',
                  'batch': True,
                  'creditor_id': 'DE26ZZZ00000000000',
                  'currency': 'EUR'},
                 id='invalid config #2 ("creditor_id" is missing)'),
    pytest.param({},
                 {'name': 'Test von Testenstein',
                  'IBAN': 'NL50BANK1234567890',
                  'BIC': 'BANKNL2A',
                  'batch': True,
                  'creditor_id': 'DE26ZZZ00000000000',
                  'currency': 'EUR'},
                 id='no config'),
])
def test_set_config(data, solution):
    res = _set_config(data)
    print('dis is res: ', res)
    print('dis is solution: ', solution)
    assert solution == res


def test_handle_output_path_wrong_path():
    temp_dir = tempfile.mkdtemp()
    dir_path = pathlib.Path(temp_dir) / 'test_out'
    res = handle_output_path(dir_path.__str__())

    assert res == dir_path.__str__() + '/'
    assert os.path.exists(os.path.dirname(res))


def test_handle_output_path_right_path():
    temp_dir = tempfile.mkdtemp('test_out/')
    dir_path = pathlib.Path(temp_dir)
    res = handle_output_path(dir_path.__str__() + '/')

    assert res == dir_path.__str__() + '/'


@pytest.mark.parametrize('f_position,solution', [
    pytest.param(0,
                 ['Jörn Balten', 'DE12345667789123959696', 'BYLEEEM1005', '0,01', 'R9875642123 07.2020',
                  '100.solarhaus', 'Vertrag: 2020202', '53012312', '31.01.2018', '31.07.2020'],
                 id='correct data'),
    pytest.param(1,
                 ['', 'DE09786512312412341232', 'BYLEEEM1005', '', 'R0000000004 07.2020',
                  '100.solarhaus', 'Vertrag: 2987653', '53009999', '17.01.2018', '31.07.2020'],
                 id='missing data (name + amount)'),
    pytest.param(3,
                 '',
                 id='no data'),
])
def test_single_csv_row(f_position, solution, test_data_path):
    t_file = open(f'{test_data_path}/bspCSV_faulty.csv', 'r')

    next(t_file)  # skip head

    res = ''
    for i, d in enumerate(single_csv_row(t_file)):
        if i == f_position:
            res = d
            break

    assert res == solution
    t_file.close()


def test_single_csv_row_empty_file(test_data_path):
    t_file = open(f'{test_data_path}/bspCSV_empty.csv', 'r')

    with pytest.raises(SystemExit) as pytest_wrap:
        for _ in single_csv_row(t_file):
            print('this fails anyways')

    assert pytest_wrap.type == SystemExit
    assert pytest_wrap.value.code == 1
    t_file.close()
