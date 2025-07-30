from django_countries import Countries as BaseCountries


EXTRA_COUNTRIES = {
    'XK': 'Kosovo',
}


class Countries(BaseCountries):
    override = EXTRA_COUNTRIES
