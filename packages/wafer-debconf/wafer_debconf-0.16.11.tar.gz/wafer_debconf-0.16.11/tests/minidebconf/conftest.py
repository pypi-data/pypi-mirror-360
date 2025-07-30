from pytest import fixture

from minidebconf import settings as mdc_settings


@fixture(autouse=True)
def minidebconf_settings(settings):
    for k, v in mdc_settings.__dict__.items():
        if k.isupper() and k not in {'DATABASES',}:
            setattr(settings, k, v)


@fixture
def attendee(db, user):
    from minidebconf.models import Registration
    attendee = Registration.objects.create(
        user=user,
        involvement=0,
        gender='n',
        country='CA',
        city_state='BC',
    )
    yield attendee
    attendee.delete()
