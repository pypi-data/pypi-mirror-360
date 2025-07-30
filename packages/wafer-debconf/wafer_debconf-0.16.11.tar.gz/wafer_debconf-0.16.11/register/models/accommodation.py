import datetime

from django.db import models
from django.conf import settings

from register.dates import get_ranges_for_dates
from register.models.attendee import Attendee


PAID_ACCOMMODATION = any(
    'price' in option for option in settings.PRICES['accomm'].values())

SELF_PAID_ACCOMMODATION = any(
    'paid_separately' in option for option in settings.PRICES['accomm'].values())


def accomm_option_choices(bursary=False, paid=False, include=None):
    """Return Django choices for accommodation options.

    bursary (bool): Include options only avaliable to bursaried attendees.
    paid (bool): Include options only available to non-bursaried attendees.
    include (str): Include the specifically named option.
    """

    for key, details in settings.PRICES['accomm'].items():
        if key != include:
            if bursary and not details.get('bursary', False):
                continue
            if paid and not details.get('price', None):
                continue

        description = details['description']
        if 'price' in details:
            description += (
                f" ({details['price']} {settings.DEBCONF_BILLING_CURRENCY}"
                f"/night)")
        yield (key, description)


class AccommNight(models.Model):
    date = models.DateField(unique=True)

    @property
    def form_name(self):
        return 'night_{}'.format(self)

    def __str__(self):
        return self.date.isoformat()

    class Meta:
        ordering = ['date']


class Accomm(models.Model):
    attendee = models.OneToOneField(Attendee, related_name='accomm',
                                    on_delete=models.CASCADE)
    nights = models.ManyToManyField(AccommNight)
    option = models.CharField(max_length=32,
                              choices=accomm_option_choices())
    requirements = models.TextField(blank=True)
    family_usernames = models.TextField(blank=True)
    room = models.CharField(max_length=128, blank=True, default='')

    def __str__(self):
        return 'Accomm <{}>'.format(self.attendee.user.username)

    def get_checkin_checkouts(self):
        """Get the successive check-in and check-out dates for the attendee"""
        stays = get_ranges_for_dates(
            night.date for night in self.nights.all()
        )

        for first_night, last_night in stays:
            yield first_night
            yield last_night + datetime.timedelta(days=1)

    def get_stay_details(self):
        """Get the check-in, check-out for each stay"""
        ci_co = iter(self.get_checkin_checkouts())
        return zip(ci_co, ci_co)

    def get_roommates(self):
        if self.room:
            # Is it a complex of rooms?
            if ":" in self.room:
                room = self.room.split(':', 1)[0]
                q = Attendee.objects.filter(accomm__room__startswith=room)
            else:
                q = Attendee.objects.filter(accomm__room=self.room)
            return q.exclude(id=self.attendee_id)
