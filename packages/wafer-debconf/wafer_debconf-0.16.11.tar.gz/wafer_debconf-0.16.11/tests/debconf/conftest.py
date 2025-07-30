from django.utils import timezone

from pytest import fixture

from debconf import settings as dc_settings


@fixture(autouse=True)
def debconf_settings(settings):
    for k, v in dc_settings.__dict__.items():
        if k.isupper() and k not in {'DATABASES',}:
            setattr(settings, k, v)
    settings.ROOT_URLCONF = 'tests.debconf.urls'
    settings.WAFER_USER_IS_REGISTERED = 'register.models.user_is_registered'


@fixture
def attendee(db, user):
    from register.models.attendee import Attendee
    attendee = Attendee.objects.create(
        user=user,
        nametag_2='Line 2',
        nametag_3='Line 3',
        emergency_contact='Emergency Contact <contact@example.com>',
        announce_me=True,
        register_announce=False,
        register_discuss=False,
        coc_ack=True,
        fee='',
        arrival=None,
        departure=None,
        final_dates=False,
        reconfirm=True,
        t_shirt_size='l',
        shoe_size='l',
        gender='n',
        country='CA',
        languages='Python',
        pgp_fingerprints='',
        invoiced_entity='',
        billing_address='Billing Address',
        notes='',
        completed_register_steps=13,
        completed_timestamp=timezone.now(),
    )
    yield attendee
    attendee.delete()


@fixture
def bursary(db, attendee):
    from bursary.models import Bursary
    bursary = Bursary.objects.create(
        user=attendee.user,
        request_travel=True,
        request_food=True,
        request_accommodation=True,
        request_expenses=False
    )
    yield bursary
    bursary.delete()
