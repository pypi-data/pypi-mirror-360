from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout


class Covid19Form(forms.Form):
    vaccinated = forms.BooleanField(
        label='I have been fully vaccinated against COVID-19',
        help_text='You are fully vaccinated if you have completed the full '
                  'course of vaccination, at least 2 weeks before arrival '
                  'at the conference venue.',
        required=False,
    )
    vaccination_notes = forms.CharField(
        label='Notes for the conference organisers',
        help_text='If you have not been vaccinated, please explain the '
                  'situation.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    confirm_covid_tests = forms.BooleanField(
        label='I agree to report any respiratory symptoms to the organisers and follow their instructions',
        help_text='You agree to report any respiratory symptoms and follow the instructions '
                  'provided by the organisers, as required by the '
                  '<a href="/about/covid19/">conference COVID-19 policy</a>.',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
        self.helper.layout = Layout(
            Field('vaccinated', id='vaccinated'),
            Field('vaccination_notes'),
            Field('confirm_covid_tests', id='confirm_covid_tests'),
        )

    def clean(self):
        cleaned_data = super().clean()
        if (not cleaned_data.get('vaccinated')
                and not cleaned_data.get('vaccination_notes')):
            self.add_error(
                'vaccination_notes',
                'Please explain the reasons for not receiving a vaccine.')
        if (not cleaned_data.get('vaccinated')
                and not cleaned_data.get('confirm_covid_tests')):
            self.add_error(
                'confirm_covid_tests',
                'Please confirm your willingness to be regularly tested')

        return cleaned_data
