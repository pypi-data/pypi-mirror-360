from django.db import models

from register.fields import RequiredCountries
from register.models.attendee import Attendee


class Visa(models.Model):
    attendee = models.OneToOneField(Attendee, related_name='visa',
                                    on_delete=models.CASCADE)
    country = models.CharField(max_length=2)

    @property
    def country_name(self):
        return RequiredCountries().name(self.country)
