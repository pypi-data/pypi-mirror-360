from datetime import date

from django.forms import ModelForm, Select
from django.forms.widgets import DateInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from register.fields import RequiredCountries

from daytrip.models import TravelInsurance


class NativeDateInput(DateInput):
    """DateInput using an HTML5 native widget"""

    input_type = "date"

    def __init__(self, attrs=None, *args, **kwargs):
        if attrs:
            for key in ("min", "max"):
                if isinstance(attrs.get(key), date):
                    attrs[key] = attrs[key].isoformat()
        super().__init__(attrs, *args, **kwargs)


class TravelInsuranceForm(ModelForm):
    class Meta:
        model = TravelInsurance
        exclude = ["attendee"]
        widgets = {
            "country": Select(
                choices=RequiredCountries(),
            ),
            "date_of_birth": NativeDateInput(
                attrs={
                    "max": date.today,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.add_input(Submit('save', 'Save'))
