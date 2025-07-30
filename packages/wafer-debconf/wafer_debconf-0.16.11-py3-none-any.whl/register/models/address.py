from django.db import models

from register.fields import RequiredCountries
from register.models.attendee import Attendee


class Address(models.Model):
    ROLE_CHOICES = (
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
    )
    attendee = models.ForeignKey(Attendee, related_name='addresses',
        on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    contact = models.CharField(max_length=50)
    company = models.CharField(max_length=50, blank=True)
    line1 = models.CharField(max_length=50)
    line2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=2)
    phone_number = models.CharField(max_length=32, blank=True)

    class Meta:
        unique_together = ('attendee', 'role')

    @property
    def country_name(self):
        return RequiredCountries().name(self.country)

    @property
    def formatted_address(self):
        output = [
            self.contact,
            f'Phone: {self.phone_number}',
            self.company,
            self.line1,
            self.line2,
            self.city,
            self.province,
            self.postal_code,
            self.country_name,
        ]
        return '\n'.join(line for line in output if line)
