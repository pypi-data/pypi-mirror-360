from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout


class MiscForm(forms.Form):
    reason_contribution = forms.CharField(
        label='My contributions to Debian',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
        help_text='To help us evaluate your registration.',
    )
    reason_plans = forms.CharField(
        label='My plans for DebCamp or DebConf',
        help_text='To help us evaluate your registration.',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
    )
    notes = forms.CharField(
        label='Special Needs and Notes for the registration team',
        help_text='Anything else you need to describe. '
                  'The registration team will see this. '
                  'The bursaries team will not.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.contributions = kwargs.pop('contributions')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

        reasons = ()
        if self.contributions:
            reasons = (
                Fieldset(
                    'Contributions to Debian',
                    Field('reason_contribution'),
                    Field('reason_plans'),
                    css_id='contributions',
                ),
            )
        self.helper.layout = Layout(
            Field('notes'),
            *reasons
        )

    def clean(self):
        cleaned_data = super().clean()

        if self.contributions:
            if not cleaned_data.get('reason_plans'):
                self.add_error(
                    'reason_plans',
                    'Please share your plans for the conference, when applying '
                    'for free attendance.')

            if not cleaned_data.get('reason_contribution'):
                self.add_error(
                    'reason_contribution',
                    'Please describe your contributions and/or the '
                    'diversity of your background, when applying for free '
                    'attendance.')
