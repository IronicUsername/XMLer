from datetime import date
import tempfile

import pytest
import xmltodict

from xmler.converter.csv_to_sepa_xml import _pack_data, _sanatize_data, create_sepa_xml


def test_create_sepa_xml(test_data_path, default_conf):
    test_file = '/bspCSV.csv'

    t_file = open(test_data_path + test_file, 'r')
    out_path = tempfile.mkdtemp(suffix='/')
    next(t_file)  # skip header
    create_sepa_xml(t_file, out_path, default_conf)

    f_name = str(date.today())
    res_debit_file = open(f'{out_path}/{f_name}_gutschrift.xml', 'r')
    res_credit_file = open(f'{out_path}/{f_name}_ueberweisung.xml', 'r')

    # check credit
    res_credit = xmltodict.parse(res_credit_file.read())['Document']['CstmrCdtTrfInitn']['PmtInf']
    assert res_credit['NbOfTxs'] == '1'
    assert res_credit['CtrlSum'] == '900.01'

    assert res_credit['CdtTrfTxInf']['Cdtr']['Nm'] == 'Peter Pan'
    assert res_credit['CdtTrfTxInf']['CdtrAcct']['Id']['IBAN'] == 'DE71278417824781247878'
    assert res_credit['CdtTrfTxInf']['RmtInf']['Ustrd'] == 'R1010101022 07.2020 100.solarhaus Vertrag: 2222222'
    res_credit_file.close()

    # check debit
    res_debit = xmltodict.parse(res_debit_file.read())['Document']['CstmrDrctDbtInitn']['PmtInf']
    assert res_debit['NbOfTxs'] == '2'
    assert res_debit['CtrlSum'] == '21.53'
    assert res_debit['Cdtr']['Nm'] == 'Test von Testenstein'
    assert res_debit['CdtrAcct']['Id']['IBAN'] == 'NL50BANK1234567890'

    assert res_debit['DrctDbtTxInf'][0]['InstdAmt']['#text'] == '0.01'
    assert res_debit['DrctDbtTxInf'][0]['Dbtr']['Nm'] == 'Joern Balten'
    assert res_debit['DrctDbtTxInf'][0]['DbtrAcct']['Id']['IBAN'] == 'DE12345667789123959696'
    assert res_debit['DrctDbtTxInf'][0]['RmtInf']['Ustrd'] == 'R9875642123 07.2020 100.solarhaus Vertrag: 2020202'

    assert res_debit['DrctDbtTxInf'][1]['InstdAmt']['#text'] == '21.52'
    assert res_debit['DrctDbtTxInf'][1]['Dbtr']['Nm'] == 'Maex Musstermann'
    assert res_debit['DrctDbtTxInf'][1]['DbtrAcct']['Id']['IBAN'] == 'DE09786512312412341232'
    assert res_debit['DrctDbtTxInf'][1]['RmtInf']['Ustrd'] == 'R0000000004 07.2020 100.solarhaus Vertrag: 2987653'
    res_debit_file.close()
    t_file.close()


def test_create_sepa_xml_only_credit(test_data_path, default_conf):
    test_file = '/bspCSV_only_credit.csv'

    t_file = open(test_data_path + test_file, 'r')
    out_path = tempfile.mkdtemp(suffix='/')
    next(t_file)  # skip header
    create_sepa_xml(t_file, out_path, default_conf)

    f_name = str(date.today())
    res_credit_file = open(f'{out_path}/{f_name}_ueberweisung.xml', 'r')

    res_credit = xmltodict.parse(res_credit_file.read())['Document']['CstmrCdtTrfInitn']['PmtInf']
    assert res_credit['NbOfTxs'] == '2'
    assert res_credit['CtrlSum'] == '435.79'

    assert res_credit['CdtTrfTxInf'][0]['Amt']['InstdAmt']['#text'] == '15.10'
    assert res_credit['CdtTrfTxInf'][0]['Cdtr']['Nm'] == 'Broe Dude'
    assert res_credit['CdtTrfTxInf'][0]['CdtrAcct']['Id']['IBAN'] == 'DE11430609672025054100'
    assert res_credit['CdtTrfTxInf'][0]['RmtInf']['Ustrd'] == 'R8875642123 07.2020 100.solarhaus Vertrag: 1420288'

    assert res_credit['CdtTrfTxInf'][1]['Amt']['InstdAmt']['#text'] == '420.69'
    assert res_credit['CdtTrfTxInf'][1]['Cdtr']['Nm'] == 'Sleepy Joe'
    assert res_credit['CdtTrfTxInf'][1]['CdtrAcct']['Id']['IBAN'] == 'DE03370502990053002614'
    assert res_credit['CdtTrfTxInf'][1]['RmtInf']['Ustrd'] == 'R0000000004 07.2020 100.solarhaus Vertrag: 7654321'
    res_credit_file.close()


def test_create_sepa_xml_only_debit(test_data_path, default_conf):
    test_file = '/bspCSV_only_debit.csv'

    t_file = open(test_data_path + test_file, 'r')
    out_path = tempfile.mkdtemp(suffix='/')
    next(t_file)  # skip header
    create_sepa_xml(t_file, out_path, default_conf)

    f_name = str(date.today())
    res_debit_file = open(f'{out_path}/{f_name}_gutschrift.xml', 'r')

    res_debit = xmltodict.parse(res_debit_file.read())['Document']['CstmrDrctDbtInitn']['PmtInf']
    assert res_debit['NbOfTxs'] == '1'
    assert res_debit['CtrlSum'] == '123.45'
    assert res_debit['Cdtr']['Nm'] == 'Test von Testenstein'
    assert res_debit['CdtrAcct']['Id']['IBAN'] == 'NL50BANK1234567890'

    assert res_debit['DrctDbtTxInf']['InstdAmt']['#text'] == '123.45'
    assert res_debit['DrctDbtTxInf']['Dbtr']['Nm'] == 'Oerange Man'
    assert res_debit['DrctDbtTxInf']['DbtrAcct']['Id']['IBAN'] == 'DE17380601864602381019'
    assert res_debit['DrctDbtTxInf']['RmtInf']['Ustrd'] == 'R073000004 07.2020 100.solarhaus Vertrag: 76754321'


@pytest.mark.parametrize('data,solution', [
    pytest.param(
        ['Dude Bro', 'IBAN1234', '987654321', '1.23', 'desc 1', 'desc 2', 'desc 3', 'some_mandate_id', '01.01.2001', '01.01.2001'],
        ({'name': 'Dude Bro', 'IBAN': 'IBAN1234', 'BIC': '987654321', 'description': 'desc 1 desc 2 desc 3', 'amount': 123, 'type': 'RCUR',
          'collection_date': date.today(), 'mandate_id': 'some_mandate_id', 'mandate_date': date(2001, 1, 1)},
         'debit'),
        id='all data',
    ),
    pytest.param(
        ['Bro Dude', 'IBAN1234', '987654321', '1.23', 'desc 1', 'desc 2', 'desc 3', 'some_mandate_id', '', ''],
        ({'name': 'Bro Dude', 'IBAN': 'IBAN1234', 'BIC': '987654321', 'description': 'desc 1 desc 2 desc 3', 'amount': 123, 'type': 'RCUR',
          'collection_date': date.today(), 'mandate_id': 'some_mandate_id', 'mandate_date': date.today()},
         'debit'),
        id='no dates, everything else',
    ),
    pytest.param(
        ['', '', '12345678910', '1.23', '', '', '', '', '', ''],
        ({'name': '', 'IBAN': '', 'BIC': '12345678910', 'description': '  ', 'amount': 123, 'type': 'RCUR',
          'collection_date': date.today(), 'mandate_id': '', 'mandate_date': date.today()},
         'debit'),
        id='essential data',
    ),
    pytest.param(
        ['Jöhn Doé Mußtermän', '', '12345678910', '-14.88', '', '', '', '', '', ''],
        ({'name': 'Joehn Doe Musstermaen', 'IBAN': '', 'BIC': '12345678910', 'description': '  ', 'amount': 1488, 'execution_date': date.today()},
         'credit'),
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
