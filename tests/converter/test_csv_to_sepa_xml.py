from datetime import date

import pytest

from xmler.converter.csv_to_sepa_xml import _generate_output, _pack_data, _sanatize_data, create_sepa_xml


def test_generate_output():
    assert True


@pytest.mark.parametrize('data,solution', [
    pytest.param(
        ['Dude Bro', 'IBAN1234', '987654321', '1.23', 'desc 1', 'desc 2', 'desc 3', 'some_mandate_id', '01.01.2001', '01.01.2001'],
        ({'name': 'Dude Bro', 'IBAN': 'IBAN1234', 'BIC': '987654321', 'description': 'desc 1 desc 2 desc 3',
          'amount': 123, 'execution_date': date(2001, 1, 1)},
         'credit'),
        id='all data',
    ),
    pytest.param(
        ['Bro Dude', 'IBAN1234', '987654321', '1.23', 'desc 1', 'desc 2', 'desc 3', 'some_mandate_id', '', ''],
        ({'name': 'Bro Dude', 'IBAN': 'IBAN1234', 'BIC': '987654321', 'description': 'desc 1 desc 2 desc 3',
          'amount': 123, 'execution_date': date.today()},
         'credit'),
        id='no dates, everything else',
    ),
    pytest.param(
        ['', '', '12345678910', '1.23', '', '', '', '', '', ''],
        ({'name': '', 'IBAN': '', 'BIC': '12345678910', 'description': '  ', 'amount': 123, 'execution_date': date.today()},
         'credit'),
        id='essential data',
    ),
    pytest.param(
        ['Jöhn Doé Mußtermän', '', '12345678910', '-14.88', '', '', '', '', '', ''],
        ({'name': 'Joehn Doe Musstermaen', 'IBAN': '', 'BIC': '12345678910', 'description': '  ', 'amount': 1488, 'type': 'RCUR',
          'collection_date': date.today(), 'mandate_id': '', 'mandate_date': date.today()}, 'debit'),
        id='name contains illegal characters + negative money amont',
    ),
])
def test_pack_data(data, solution):
    res = _pack_data(data)
    assert solution == res


@pytest.mark.parametrize('data,solution', [
    pytest.param(['Ömer Êfghïj', '', '1234', '9876 €', 'desc1', 'desc2', 'desc3', '', '', ''],
                 ['Oemer Efghij', '', '1234', '9876 ', 'desc1 desc2 desc3', '', date.today(), date.today()],
                 id='umlauts and other illegal characters in name and money amount'),
    pytest.param(['', '', '1234', '9876', '', '', '', '', '31.08.3030', '30.06.2033'],
                 ['', '', '1234', '9876', '  ', '', date(3030, 8, 31), date(2033, 6, 30)],
                 id='mandate date and execution date'),
    pytest.param(['', 'DE85370100500123456503', '', '9876', '', '', '', '', '', ''],
                 ['', 'DE85370100500123456503', 'PBNKDEFFXXX', '9876', '  ', '', date.today(), date.today()],
                 id='find correct BIC from IBAN'),
])
def test_sanatize_data(data, solution):
    res = _sanatize_data(data)
    assert solution == res
