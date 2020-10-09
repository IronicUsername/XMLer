from schema import And, Schema

CONFIG = {
    'name': 'Test von Testenstein',
    'IBAN': 'NL50BANK1234567890',
    'BIC': 'BANKNL2A',
    'batch': True,
    'creditor_id': 'DE26ZZZ00000000000',  # supplied by your bank or financial authority
    'currency': 'EUR',  # ISO 4217
}

CONF_STRUC = Schema({
    'name': And(str),
    'IBAN': And(str),
    'BIC': And(str),
    'batch': And(bool),
    'creditor_id': And(str),
    'currency': And(str),
})
