from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import Form, fields, widgets
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, HTML, Layout, Submit

from invoices.prices import meal_prices, meal_price_string
from register.dates import conference_dinner_meal, meal_choices
from register.fields import MealSelectionField


class SearchForm(Form):
    q = fields.CharField(label='Find Users', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.include_media = False
        self.helper.add_input(Submit('search', 'Search'))


class CheckInForm(Form):
    t_shirt = fields.BooleanField(label='T-shirt', required=False)
    shoes = fields.BooleanField(label='Shoes', required=False)
    swag = fields.BooleanField(label='Swag Bag', required=False)
    nametag = fields.BooleanField(required=False)
    room_key = fields.BooleanField(required=False)
    meal_vouchers = fields.BooleanField(required=False)
    bedding = fields.BooleanField(label='Bedding', required=False)
    transit_card = fields.BooleanField(label='Transit Card', required=False)
    notes = fields.CharField(
        required=False,
        widget=widgets.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        if settings.DEBCONF_SHOE_SIZES:
            shoes = ('shoes',)
        else:
            shoes = ()
        self.helper.layout = Layout(
            't_shirt',
            *shoes,
            'swag',
            'nametag',
            'room_key',
            'meal_vouchers',
            'bedding',
            'transit_card',
        )
        self.helper.layout.fields += [
            'notes',
            ButtonHolder(
                Submit('submit', 'Check In'),
                HTML('<a href="{}" class="btn btn-secondary">Cancel</a>'
                     .format(reverse('front_desk'))),
            ),
        ]


class CheckOutForm(Form):
    returned_key = fields.BooleanField(
        label='Returned Room Key', required=False)
    returned_card = fields.BooleanField(
        label='Returned Dorm Card', required=False)
    returned_bedding = fields.BooleanField(
        label='Returned Bedding', required=False)
    notes = fields.CharField(
        required=False,
        widget=widgets.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.layout = Layout(
            'returned_key',
            'returned_card',
            'returned_bedding',
            'notes',
            ButtonHolder(
                Submit('submit', 'Check Out'),
                HTML('<a href="{}" class="btn btn-secondary">Cancel</a>'
                     .format(reverse('front_desk'))),
            ),
        )


class TShirtForm(Form):
    size = fields.ChoiceField(
        label='T-shirt',
        choices=settings.DEBCONF_T_SHIRT_SIZES,
        required=False,
    )

    def __init__(self, *args, username, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse(
            'front_desk.change_shirt', kwargs={'username': username})
        self.helper.include_media = False
        self.helper.add_input(Submit('update', 'Update Shirt'))


class ShoesForm(Form):
    size = fields.ChoiceField(
        label='Shoes',
        choices=settings.DEBCONF_SHOE_SIZES,
        required=False,
    )

    def __init__(self, *args, username, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse(
            'front_desk.change_shoes', kwargs={'username': username})
        self.helper.include_media = False
        self.helper.add_input(Submit('update', 'Update Shoes'))


class RegisterOnSiteForm(Form):
    name = fields.CharField()
    username = fields.CharField(validators=[
        validators.RegexValidator(
            r'^[\w.@+-]+$',
            'Enter a valid username. This value may contain only letters, '
            'numbers and @/./+/-/_ characters.',
            'invalid')
        ])
    email = fields.EmailField()
    departure = fields.DateTimeField()
    coc_ack = fields.BooleanField(label='Agrees to abide by CoC')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        layout = self.helper.build_default_layout(self)
        layout.fields.append(
            ButtonHolder(
                Submit('register', 'Register'),
                HTML('<a href="{}" class="btn btn-secondary">Cancel</a>'
                     .format(reverse('front_desk'))),
            )
        )
        self.helper.add_layout(layout)

    def clean_username(self):
        username = self.cleaned_data['username']
        if get_user_model().objects.filter(username=username).exists():
            raise ValidationError('User with this username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError('User with this email already exists')
        return email


class CashInvoicePaymentForm(Form):
    receipt_number = fields.IntegerField()
    amount = fields.DecimalField(max_digits=8, decimal_places=2,
                                 validators=[validators.MinValueValidator(0)])

    def __init__(self, *args, instance, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.helper = FormHelper()
        self.helper.include_media = False
        layout = self.helper.build_default_layout(self)
        layout.fields.append(
            ButtonHolder(
                Submit('pay', 'Record Payment'),
                HTML(
                    '<a href="{}" class="btn btn-secondary">Cancel</a>'
                    .format(reverse(
                        'front_desk.check_in',
                        kwargs={'username': self.instance.recipient.username},
                    )))))
        self.helper.add_layout(layout)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        expected_amount = self.instance.total
        if amount != expected_amount:
            raise ValidationError(
                f'The invoice was for {expected_amount} '
                f'{settings.DEBCONF_BILLING_CURRENCY}')
        return amount


class FoodForm(Form):
    meals = fields.MultipleChoiceField(
        choices=meal_choices(),
        widget=widgets.CheckboxSelectMultiple,
        help_text="If you don't have a food bursary, meal prices are: {}"
                  .format(meal_price_string()),
        required=False,
    )
    conference_dinner = fields.BooleanField(
        label='Conference Dinner',
        help_text="If you don't have a food bursary, the conference dinner "
                  "will cost {conference_dinner} {currency}."
                  .format(**meal_prices()),
        required=False,
    )

    def __init__(self, *args, instance, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        self.helper = FormHelper()
        self.helper.include_media = False

        conference_dinner = ()
        if conference_dinner_meal():
            conference_dinner = (Field('conference_dinner'),)

        self.helper.layout = Layout(
            MealSelectionField('meals', id='meals'),
            *conference_dinner,
            HTML('<div class="alert alert-success">'
                 f'Total: {settings.DEBCONF_BILLING_CURRENCY}'
                 '<span id="total">0.00</span>. '
                 '<span style="display: none">'
                 f'Difference: {settings.DEBCONF_BILLING_CURRENCY}'
                 '<span id="delta">0.00</span>'
                 '</span></div>'),
            ButtonHolder(
                Submit('save', 'Save'),
                HTML(
                    '<a href="{}" class="btn btn-secondary">Cancel</a>'
                    .format(reverse(
                        'front_desk.check_in',
                        kwargs={'username': self.instance.user.username},
                    )))),
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.pop('conference_dinner'):
            cleaned_data['meals'].append(conference_dinner_meal())
