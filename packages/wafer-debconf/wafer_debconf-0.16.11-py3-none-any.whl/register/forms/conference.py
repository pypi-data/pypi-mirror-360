from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, HTML, Layout

from register.models import Attendee
from register.dates import (
    ARRIVE_ON_OR_AFTER, ORGA_ARRIVE_ON_OR_AFTER, LEAVE_ON_OR_BEFORE
)


INVOICE_GENERATED_ERROR = (
    'Your invoice has already been generated, '
    'contact the registration team if you need to update it.'
)
FINAL_DATES_ESTIMATE_LABEL = "Estimated, I haven't booked travel yet."
FINAL_DATES_FINAL_LABEL = 'Final, I have booked my travel.'


class ConferenceRegistrationForm(forms.Form):
    coc_ack = forms.BooleanField(
        label=mark_safe(
            'I have read and promise to abide by the '
            '<a href="https://www.debconf.org/codeofconduct.shtml" '
            'target="_blank">DebConf Code of Conduct</a>'
        ),
        required=True,
    )
    fee = forms.ChoiceField(
        label='My registration fee',
        choices=Attendee.FEES.items(),
        help_text='We encourage attendees to pay for their attendance if they '
                  'can afford to do so.',
        widget=forms.RadioSelect,
        initial='pro',
        required=False,
    )
    arrival = forms.DateTimeField(
        label='I arrive at the venue on',
        help_text="Please estimate, if you haven't booked tickets, yet, "
                  'and update it when you have final dates.',
        required=False,
    )
    departure = forms.DateTimeField(
        label='I depart from the venue on',
        help_text=f"The date picker won't let you go beyond "
                  f"{settings.DEBCONF_DEPARTURE_TIME} on the departure day.",
        required=False,
    )
    final_dates = forms.BooleanField(
        label='My dates are',
        widget=forms.Select(choices=(
                (False, FINAL_DATES_ESTIMATE_LABEL),
                (True, FINAL_DATES_FINAL_LABEL),
        )),
        initial=False,
        help_text="We'd like a rough indication of dates, even if you aren't "
                  'sure about the details yet. It helps us to plan.',
        required=False,
    )
    reconfirm = forms.BooleanField(
        label='I confirm my attendance',
        help_text="If you do not select this by "
                  f"{settings.DEBCONF_CONFIRMATION_DEADLINE.isoformat()} AoE, "
                  "we'll assume you aren't coming. If you are a paying "
                  "attendee, checking this box will generate your invoice.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        attendee = kwargs.pop('attendee')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

        self.orga_dates = attendee.user.has_perm('register.orga_early_arrival')

        dates_list = []
        for label, start, end in settings.DEBCONF_DATES:
            dates_list.append('<dt>{}:</dt>'.format(label))
            if start == end:
                dates_list.append('<dd>{}</dd>'.format(start))
            else:
                dates_list.append('<dd>{} to {}</dd>'.format(start, end))

        if settings.DEBCONF_ONLINE:
            del self.fields['arrival']
            del self.fields['departure']
            del self.fields['final_dates']
            self.helper.layout = Layout(
                'coc_ack',
                'fee',
            )
        else:
            self.helper.layout = Layout(
                'coc_ack',
                'fee',
                Fieldset(
                    'Dates',
                    HTML('<dl>' + ''.join(dates_list) + '</dl>'
                         '<p>'
                         '  <a href="/schedule/important-dates/" target="_blank">'
                         '    Important Dates'
                         '  </a>'
                         '</p>'),
                    Field('arrival', id='arrival'),
                    Field('departure', id='departure'),
                    'final_dates',
                    id="dates",
                ),
            )
        if settings.RECONFIRMATION:
            self.helper.layout.append('reconfirm')

    def clean(self):
        cleaned_data = super().clean()

        if not settings.DEBCONF_ONLINE:
            if self.orga_dates:
                arrive_on_or_after = ORGA_ARRIVE_ON_OR_AFTER
            else:
                arrive_on_or_after = ARRIVE_ON_OR_AFTER

            arrival = cleaned_data.get('arrival')
            if arrival and arrival.date() < arrive_on_or_after:
                self.add_error(
                    'arrival', f"Cannot arrive before {arrive_on_or_after}")

            departure = cleaned_data.get('departure')
            if departure and departure.date() > LEAVE_ON_OR_BEFORE:
                self.add_error(
                    'departure', f"Cannot depart after {LEAVE_ON_OR_BEFORE}")

            if arrival and departure and arrival > departure:
                self.add_error('arrival', 'Cannot arrive after departure')
                self.add_error('departure', 'Cannot depart before arrival')

            if cleaned_data.get('final_dates'):
                for field in ('arrival', 'departure'):
                    if not cleaned_data.get(field):
                        self.add_error(
                            field, 'If your dates are final, please provide them')

            else:
                if cleaned_data.get('reconfirm'):
                    self.add_error(
                        'final_dates', 'Dates need to be final, to reconfirm')
