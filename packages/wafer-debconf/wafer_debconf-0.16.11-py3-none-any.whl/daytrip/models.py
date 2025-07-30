from django.db import models

from register.models import Attendee


class TravelInsurance(models.Model):
    attendee = models.OneToOneField(Attendee, related_name='travel_insurance',
        on_delete=models.PROTECT)
    surname = models.CharField(max_length=100,
        help_text="As shown in passport / ID")
    given_names = models.CharField(max_length=100,
        help_text="As shown in passport / ID")
    country = models.CharField(max_length=2)
    passport_no = models.CharField(max_length=100,
        help_text="Or local ID number for local citizens")
    gender = models.CharField(max_length=20,
        help_text="As shown in passport / ID")
    date_of_birth = models.DateField()
