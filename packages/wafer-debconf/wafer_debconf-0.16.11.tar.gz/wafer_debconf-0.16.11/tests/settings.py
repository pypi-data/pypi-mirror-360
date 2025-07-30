from datetime import date

# A basic set of settings that is applicable for both test suites.
# Many of these will be overridden by conftest.py in the suites.

from debconf.common_settings import *

INSTALLED_APPS = (
    # minidebconf:
    'minidebconf',
    # debconf:
    'badges',
    'daytrip',
    'debconf',
    'exports',
    'bursary',
    'front_desk',
    'invoices',
    'register',
    'volunteers',
) + INSTALLED_APPS

# For MiniDebConf Tests:

# For DebConf Tests:
DEBCONF_BREAKFAST = True
DEBCONF_NAME = 'Test DebConf'
DEBCONF_DATES = (
    ('DebCamp', date(2003, 7, 12), date(2003, 7, 17)),
    ('DebConf', date(2003, 7, 18), date(2003, 7, 20)),
)
DEBCONF_CONFIRMATION_DEADLINE = date(2003, 6, 15)
DEBCONF_LOCAL_CURRENCY_RATE = 1
DEBCONF_T_SHIRT_SIZES = (
    ('', 'No T-shirt'),
    ('s', 'Small'),
    ('l', 'Large'),
)
DEBCONF_SHOE_SIZES = (
    ('', 'No Shoes'),
    ('s', 'Small'),
    ('l', 'Large'),
)

INVOICE_PREFIX = 'DCTEST-'
PRICES = {
    'fee': {
        '': {
            'name': 'Regular',
            'price': 0,
        },
        'pro': {
            'name': 'Professional',
            'price': 10,
        },
    },
    'meal': {
        'breakfast': {
            'price': 1,
        },
        'lunch': {
            'price': 3,
        },
        'dinner': {
            'price': 5,
        },
        'conference_dinner': {
            'price': 7,
        },
    },
    'accomm': {},
}
STRIPE_SECRET_KEY = ''
