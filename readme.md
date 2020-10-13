### XMLer
Converts CSV files to SEPA validated XML.

## prerequisite
You have to create a `config.json` in the project root.<br>

`config.json`:
```json
{
    "name": "Test von Testenstein",
    "IBAN": "NL50BANK1234567890",
    "BIC": "BANKNL2A",
    "batch": True,
    "creditor_id": "DE26ZZZ00000000000",
    "currency": "EUR"
}
```
Notes:
- `creditor_id`: supplied by your bank or financial authority
- `currency`: has to be in `ISO 4217` format

## install & run
Basic usage:
```bash
xmler PATH/TO/FILE.csv
```

Arguments:
- `-o` / `--output` = SEPA XML output path.
- `--header` / `--no-header` = If the your CSV file contains the table header it will be removed. The script <b>removes the header by default.</b>

## development
In order to work on XMLer you need to have [poetry](https://poetry.eustace.io/docs/#installation) installed on your system.<br>
You install the application with
```bash
poetry install
```

and access the virtual environment
```bash
poetry shell
```
<br>

Run tests with
```bash
pytest -vvv
```

and for code checks you can do
```bash
flake8 src && mypy src && pydocstyle src
```
