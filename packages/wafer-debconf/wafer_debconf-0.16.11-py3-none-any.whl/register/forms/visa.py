from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, HTML, Layout
from django_countries.fields import LazyTypedChoiceField

from register.fields import CitizenshipCountries


class VisaForm(forms.Form):
    visa = forms.BooleanField(
        label='I require a visa to travel to DebConf',
        required=False,
        help_text='See <a href="/about/visas/">the visa page</a> for details',
    )
    country = LazyTypedChoiceField(
        label='My citizenship',
        help_text='I will apply for a visa as a citizen of the specified '
                  'country.',
        choices=CitizenshipCountries(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

        self.helper.layout = Layout(
            Field('visa', id='visa'),
            Fieldset(
                'Visa Details',
                HTML(
                    'Please contact the visa team at '
                    '<a href="mailto:visa@debconf.org">visa@debconf.org</a> '
                    'for advice or assistance in obtaining a visa to travel '
                    'to DebConf.'),
                'country',
                css_id='details',
            ),
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('visa') and not cleaned_data.get('country'):
            self.add_error(
                'country',
                'Please provide us with your country of citizenship.')

        return cleaned_data
