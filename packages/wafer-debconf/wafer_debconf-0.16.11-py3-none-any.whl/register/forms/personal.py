import re

from django.conf import settings
from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, HTML
from django_countries.fields import LazyTypedChoiceField

from register.fields import OptionalCountries, RequiredCountries, CitizenshipCountries
from register.models.attendee import Attendee


T_SHIRT_CHART_LINK = '<a href="/about/t-shirts" target="_blank">t-shirt sizes chart</a>'
SHOE_CHART_LINK = '<a href="/about/shoe-sizes target="_blank"">shoe size chart</a>'


class PersonalInformationForm(forms.Form):
    t_shirt_size = forms.ChoiceField(
        label='My t-shirt size',
        choices=settings.DEBCONF_T_SHIRT_SIZES,
        help_text=(
            f'Refer to the {T_SHIRT_CHART_LINK}. The fitted cut is sized for '
            f'a smaller-framed and curvier body type than the straight cut, '
            f'so they run about two sizes smaller in width than the '
            f'straight-cut sizes, and are also rather shorter in length.'
        ),
        required=False,
    )
    shoe_size = forms.ChoiceField(
        label='My shoe size',
        choices=settings.DEBCONF_SHOE_SIZES,
        help_text='Refer to the ' + SHOE_CHART_LINK + '.',
        required=False,
    )
    shipping_contact = forms.CharField(
        label='Recipient Name',
        help_text='Required. Addressee for the package',
        max_length=50,
        required=False,
    )
    shipping_phone_number = forms.CharField(
        label='Phone Number',
        help_text='Optional, but strongly recommended. '
                  'Useful for customs and couriers to contact you.',
        max_length=32,
        required=False,
    )
    shipping_company = forms.CharField(
        label='Company Name',
        help_text='Optional, use if shipping to a company.',
        max_length=50,
        required=False,
    )
    shipping_line1 = forms.CharField(
        label='Address Line 1',
        help_text='Required. Usually the street name and number.',
        max_length=50,
        required=False,
    )
    shipping_line2 = forms.CharField(
        label='Address Line 2',
        help_text='Optional, usually the district / suburb',
        max_length=50,
        required=False,
    )
    shipping_city = forms.CharField(
        label='City/Town',
        max_length=50,
        required=False,
        help_text='Required',
    )
    shipping_province = forms.CharField(
        label='State/Province',
        max_length=50,
        required=False,
        help_text='Required',
    )
    shipping_postal_code = forms.CharField(
        label='Postal/ZIP Code',
        max_length=32,
        required=False,
    )
    shipping_country = LazyTypedChoiceField(
        label='Country',
        choices=RequiredCountries(),
        required=False,
        help_text='Required',
    )
    gender = forms.ChoiceField(
        label='My gender',
        choices=Attendee.GENDERS.items(),
        help_text='For diversity statistics.',
        required=False,
    )
    country = LazyTypedChoiceField(
        label='The country I call home',
        help_text='For diversity statistics.',
        choices=OptionalCountries(),
        required=False,
    )
    affiliation = forms.CharField(
        label='My affiliation (e.g. employer)',
        help_text='Your affiliation will be shared with government sponsors '
                  'who count foreign attendees',
        required=False,
    )
    languages = forms.CharField(
        label='The languages I speak',
        help_text='We will list these on your name-tag.',
        initial='en',
        max_length=50,
        required=False,
    )
    pgp_fingerprints = forms.CharField(
        label='My PGP key fingerprints for keysigning',
        help_text='Optional. One fingerprint per line, if you want to take '
                  'part in <a href="/about/ksp/" target="_blank">the continuous keysigning party</a>. '
                  'Will appear on nametags and a keysigning notesheet, with '
                  'no verification done by the conference organisers.<br>'
                  'Just provide the fingerprints, e.g. <code>1234 5678 90AB '
                  'CDEF 0000  1111 2222 3333 4444 5555</code>',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
    )

    full_legal_name = forms.CharField(
        label='Full legal name',
        help_text='Your full name, as presented in a government-issued ID (e.g. your passport)',
        max_length=256,
        required=settings.DEBCONF_SECURITY_INFO,
    )
    date_of_birth = forms.DateField(
        label='Date of birth',
        help_text='Your birth date',
        required=settings.DEBCONF_SECURITY_INFO,
    )
    country_of_citizenship = LazyTypedChoiceField(
        label='Country of citizenship',
        help_text='If none, select "Stateless"',
        choices=CitizenshipCountries(),
        required=settings.DEBCONF_SECURITY_INFO,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
        if settings.DEBCONF_SECURITY_INFO:
            security_disclaimer = HTML(
                '<p>'
                'Due to requirements imposed by the local authorities, '
                'we are compelled to collect this information. '
                'This data will only be available to a member of the local '
                'team and school personnel with security clearance.'
                '</p>'
            )
            security_personal_info = (
                Fieldset(
                    'Security-related information',
                    security_disclaimer,
                    'full_legal_name',
                    Field('date_of_birth', id='date_of_birth'),
                    'country_of_citizenship',
                    css_class="alert alert-info",
                ),
            )
        else:
            security_personal_info = ()
        if settings.DEBCONF_SHOE_SIZES:
            shoe_size = (Field('shoe_size'),)
        else:
            shoe_size = ()
        if settings.DEBCONF_ONLINE:
            shipping_address = (
                Fieldset(
                    'Shipping Address for swag (e.g. t-shirts)',
                    'shipping_contact',
                    'shipping_phone_number',
                    'shipping_company',
                    'shipping_line1',
                    'shipping_line2',
                    'shipping_city',
                    'shipping_province',
                    'shipping_postal_code',
                    'shipping_country',
                    css_id='shipping_address',
                ),
            )
        else:
            shipping_address = ()
        if settings.DEBCONF_COLLECT_AFFILIATION:
            affiliation = (Field('affiliation'),)
        else:
            affiliation = ()
        self.helper.layout = Layout(
            *security_personal_info,
            Fieldset(
                'Demographic Information',
                Field('gender'),
                Field('country'),
                *affiliation,
            ),
            Fieldset(
                'Swag',
                Field('t_shirt_size', id='t_shirt_size'),
                *shoe_size,
            ),
            *shipping_address,
        )
        if not settings.DEBCONF_ONLINE:
            self.helper.layout.append('languages'),
            self.helper.layout.append('pgp_fingerprints'),

    def clean(self):
        cleaned_data = super().clean()
        if settings.DEBCONF_ONLINE and (
                cleaned_data.get('t_shirt_size')
                or cleaned_data.get('shoe_size')):
            for field in (
                        'shipping_contact',
                        'shipping_line1',
                        'shipping_city',
                        'shipping_province',
                        'shipping_country',
                    ):
                if not cleaned_data.get(field):
                    self.add_error(field, 'Required.')

    def clean_pgp_fingerprints(self):
        fingerprints = self.cleaned_data.get('pgp_fingerprints').strip()
        if not fingerprints:
            return ''
        if '-----BEGIN' in fingerprints:
            raise ValidationError('Only fingerprints, not keys, please')
        cleaned = []
        for line in fingerprints.splitlines():
            fp = line.strip().upper().replace(' ', '')
            if fp.startswith('0x'):
                fp = fp[2:]
            if not re.match(r'^[0-9A-F]{40}$', fp):
                raise ValidationError(
                    '{} is not a PGP fingerprint'.format(line))
            cleaned.append('{} {} {} {} {}  {} {} {} {} {}'.format(
                *[fp[i:i + 4] for i in range(0, 40, 4)]))
        return '\n'.join(cleaned)
