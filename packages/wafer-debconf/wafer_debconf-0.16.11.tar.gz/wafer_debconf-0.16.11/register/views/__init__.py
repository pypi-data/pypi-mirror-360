from django.conf import settings
from register.views.accommodation import AccommodationView
from register.views.attendee import ContactInformationView
from register.views.billing import BillingView
from register.views.bursary import BursaryView
from register.views.childcare import ChildCareView
from register.views.conference import ConferenceRegistrationView
from register.views.confirmation import ConfirmationView
from register.views.covid19 import Covid19View
from register.views.food import FoodView
from register.views.instructions import InstructionsView
from register.views.misc import MiscView
from register.views.personal import PersonalInformationView
from register.views.review import ReviewView
from register.views.visa import VisaView


if settings.DEBCONF_ONLINE:
    STEPS = [
        InstructionsView,
        ContactInformationView,
        ConferenceRegistrationView,
        PersonalInformationView,
        BursaryView,
        MiscView,
        ReviewView,
        BillingView,
        ConfirmationView,
    ]
else:
    STEPS = [
        InstructionsView,
        ContactInformationView,
        ConferenceRegistrationView,
        Covid19View,
        PersonalInformationView,
        VisaView,
        BursaryView,
        FoodView,
        AccommodationView,
        ChildCareView,
        MiscView,
        ReviewView,
        BillingView,
        ConfirmationView,
    ]
