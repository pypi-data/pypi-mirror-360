from django import forms
from django.conf import settings

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, HTML

from register.dates import night_choices
from register.fields import NightSelectionField
from register.models import Accomm
from register.models.accommodation import (
        PAID_ACCOMMODATION, SELF_PAID_ACCOMMODATION, accomm_option_choices)
from bursary.models import Bursary


class AccommodationForm(forms.Form):
    accomm = forms.BooleanField(
        label='I need conference-organised accommodation',
        widget=forms.Select(choices=(
            (False, 'No, I will find my own accommodation'),
            (True, 'Yes, I need accommodation'),
        )),
        required=False,
    )
    nights = forms.MultipleChoiceField(
        label="I'm requesting accommodation for these nights:",
        help_text='The "night of" is the date of the day before a night. '
                  'So accommodation on the night of 6 Aug ends on the '
                  'morning of the 7th.',
        choices=night_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    option = forms.ChoiceField(
        label="Which accommodation would you like?",
        help_text='Different accommodation options may have different costs. '
                  'See: <a href="/about/accommodation">here</a> for details.',
        choices=accomm_option_choices(),
        required=False,
    )
    requirements = forms.CharField(
        label='Do you have any particular accommodation requirements?',
        help_text='Anything that you want us to consider for room attribution '
                  'should be listed here (ex. "I want to be with Joe Hill", '
                  '"I snore", "I go to bed early", "I need wheelchair access")',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    family_usernames = forms.CharField(
        label='Usernames of my family members, '
              'who have registered separately',
        help_text="One per line. This isn't validated.",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        attendee = kwargs.pop('attendee')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

        try:
            self.bursary = attendee.user.bursary
        except Bursary.DoesNotExist:
            self.bursary = Bursary()

        self.orga_nights = attendee.user.has_perm('register.orga_early_arrival')

        if PAID_ACCOMMODATION:
            prices = [option['price'] for option
                      in settings.PRICES['accomm'].values()
                      if 'price' in option]
            cheapest = min(prices)
            from_ = 'from ' if len(set(prices)) > 1 else ''
            accomm_availability = HTML(
                f'<p>The cost is {from_}{cheapest} '
                f'{settings.DEBCONF_BILLING_CURRENCY}/night for attendees who '
                f'do not receive a bursary. '
                f'Make sure to check "I want to apply for an accommodation '
                f'bursary" on the bursary page if you need one.</p>')
        else:
            body = (
                '<p>Conference-organised accommodation is only available to '
                'attendees who receive an accommodation bursary. If you are '
                'paying for your own accommodation, see our '
                '<a href="/about/accommodation">list of nearby options</a>.')
            if SELF_PAID_ACCOMMODATION:
                body += (
                    '<p>If you are booking self-paid accommodation with our '
                    'venue, you will need to pay them separately. '
                    "Your registration won't be complete until you have booked "
                    'and paid the venue directly.</p>'
                )
            accomm_availability = HTML(body)

        try:
            accomm_option = attendee.accomm.option
        except Accomm.DoesNotExist:
            accomm_option = None

        option = ()
        if len(settings.PRICES['accomm']) > 1:
            potential_bursary = self.bursary.potential_bursary('accommodation')
            self.fields['option'].choices = accomm_option_choices(
                bursary=potential_bursary,
                paid=not potential_bursary,
                include=accomm_option)
            option = (Field('option'),)
        if self.orga_nights:
            self.fields['nights'].choices = night_choices(orga=True)

        if settings.DEBCONF_ACCOMMODATION_CLOSED and not accomm_option:
            self.helper.layout = Layout(
                HTML('<div class="alert alert-warning">'
                '<strong>Accommodation registration is now closed.</strong> '
                'Sorry, we are unable to accommodate any additional attendees.'
                '</div>'
            ))
        elif PAID_ACCOMMODATION or self.bursary.request_accommodation or (
                SELF_PAID_ACCOMMODATION and accomm_option):
            self.helper.layout = Layout(
                accomm_availability,
                Field('accomm', id='accomm'),
                Fieldset(
                    'Accommodation Details',
                    NightSelectionField('nights'),
                    *option,
                    Field('requirements'),
                    Field('family_usernames'),
                    css_id='accomm-details',
                )
            )
        else:
            self.helper.layout = Layout(accomm_availability)

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('accomm'):
            if self.bursary.request_accommodation:
                self.add_error('accomm',
                    'Accommodation bursary was requested, but no accommodation '
                    'selected.')
            return cleaned_data

        if (not PAID_ACCOMMODATION
                and not SELF_PAID_ACCOMMODATION
                and not self.bursary.request_accommodation):
            self.add_error(
                'accomm',
                'Accommodation is only available to attendees who receive an '
                'accommodation bursary.')

        if not cleaned_data.get('nights'):
            self.add_error(
                'accomm',
                'Please select the nights you require accommodation for.')

        # We don't display the selector if there's only one option
        if len(settings.PRICES['accomm']) == 1:
            cleaned_data['option'] = list(settings.PRICES['accomm'].keys())[0]

        return cleaned_data
