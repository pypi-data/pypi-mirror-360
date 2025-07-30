from django.test import Client
from minidebconf.models import Registration
from minidebconf.forms import register_form_factory
from wafer.schedule.models import ScheduleBlock
from pytest import fixture
import pytest


@fixture
def days(db):
    day1 = ScheduleBlock.objects.create(start_time='2020-06-01 09:00+00', end_time='2020-06-01 18:00+00')
    day2 = ScheduleBlock.objects.create(start_time='2020-06-02 09:00+00', end_time='2020-06-02 18:00+00')
    day3 = ScheduleBlock.objects.create(start_time='2020-06-03 09:00+00', end_time='2020-06-03 18:00+00')
    return [day1, day2, day3]



class TestRegistrationModel:

    def test_full_name(self, user):
        registration = Registration(user=user)
        assert registration.full_name == "Firstname Lastname"


class TestRegistrationForm:

    def test_basics(self, user, days):
        form = register_form_factory()(
            instance=Registration(user=user),
            initial={"days": days}
        )
        assert not form.errors

    def test_get_full_name_from_user(self, user, days):
        registration = Registration.objects.create(user=user, country="BR")
        registration.days.add(days[0])
        form = register_form_factory()(instance=registration)
        assert form.fields['full_name'].initial == registration.full_name

    def test_pass_full_name_on_to_user(self, user, days):
        form = register_form_factory()(
            instance=Registration(user=user),
            data={"days": days, "country": "BR", "full_name": 'Foo Bar'},
        )
        assert not form.errors
        form.save()
        user.refresh_from_db()
        assert user.first_name == "Foo"
        assert user.last_name == "Bar"

    def test_phone_number_not_present_by_default(self, user):
        form = register_form_factory()(instance=Registration(user=user))
        assert 'phone_number' not in form.fields

    def test_phone_number_not_required(self, user, settings):
        settings.MINIDEBCONF_REGISTER_PHONE = False
        form = register_form_factory()(instance=Registration(user=user))
        assert not form.fields['phone_number'].required

    def test_phone_number_required(self, user, settings):
        settings.MINIDEBCONF_REGISTER_PHONE = True
        form = register_form_factory()(instance=Registration(user=user))
        assert form.fields['phone_number'].required

    def test_phone_number_invalid(self, user, settings):
        settings.MINIDEBCONF_REGISTER_PHONE = False
        form = register_form_factory()(
            instance=Registration(user=user),
            data={"phone_number": 'letters'}
        )
        assert 'phone_number' in form.errors

    @pytest.mark.parametrize(
        "phone",
        [
            # Brazil
            '5571987654321',
            '+55 71 987654321',
            '+55 (71) 987654321',
            '+55 (71) 9876-54321',
            '557139876543',
            '71987654321',
            '71 987654321',
            '(71) 987654321',
            # India
            '9775876662',
            '0 9754845789',
            '91 9857842356',
            '919578965389',
        ]
    )
    def test_phone_number_valid(self, user, settings, phone):
        settings.MINIDEBCONF_REGISTER_PHONE = True
        form = register_form_factory()(
            instance=Registration(user=user),
            data={"phone_number": phone}
        )
        assert 'phone_number' not in form.errors


class TestRegistrationView:
    def test_register(self, user, client, days):
        response = client.post(
            '/register/',
            {
                "days": [days[1].id, days[2].id],
                "country": "BR",
                "full_name": "Foo Bar",
            }
        )
        assert response.status_code == 302
        registration = Registration.objects.last()
        assert registration.user == user
        assert days[0] not in registration.days.all()
        assert days[1] in registration.days.all()
        assert days[2] in registration.days.all()

    def test_update_registration(self, user, client, days):
        record = Registration.objects.create(user=user, country="BR")
        record.days.add(days[0])
        response = client.post(
            '/register/',
            {
                "days": [days[1].id],
                "country": "FR",
                "full_name": "Baz Qux",
            }
        )
        assert response.status_code == 302
        registration = Registration.objects.get(user=user)
        assert registration.days.get() == days[1]
        assert registration.country == "FR"

    def test_unauthenticated(self, db):
        client = Client()
        response = client.get("/register/")
        assert response.status_code == 302
        assert response["Location"].startswith("/accounts/login/")


class TestCancelRegistrationView:
    def test_cancel_registration(self, user, client):
        record = Registration.objects.create(user=user)
        response = client.post('/unregister/')
        assert response.status_code == 302
        assert Registration.objects.filter(user=user).count() == 0

    def test_cancel_registration_get(self, user, client):
        record = Registration.objects.create(user=user)
        response = client.get('/unregister/')
        assert response.status_code == 200


class TestClosedRegistration:
    def test_registration_forbidden(self, user, client, settings):
        settings.WAFER_REGISTRATION_OPEN = False
        response = client.get("/register/")
        assert response.status_code == 403
