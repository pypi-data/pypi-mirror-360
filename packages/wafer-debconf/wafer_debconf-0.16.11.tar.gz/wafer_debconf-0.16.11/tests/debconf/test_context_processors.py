from datetime import timedelta
from django.utils import timezone
import pytest

from wafer.schedule.models import ScheduleBlock
from debconf.context_processors import expose_settings
from debconf.context_processors import is_it_debconf


class TestExposeSettings:
    def test_expose_settings(self, mocker):
        request = mocker.MagicMock()
        context = expose_settings(request)
        assert type(context) is dict


def create_schedule(confday):
     ScheduleBlock.objects.create(
         start_time=confday + timedelta(hours=10),
         end_time=confday + timedelta(hours=18)
    )


@pytest.fixture()
def today(now):
    return timezone.make_aware(timezone.datetime(now.year, now.month, now.day))


class TestIsItDebConf:

    def test_no_schedule_yet(self, db):
        assert is_it_debconf(None) == {}

    def test_a_month_before_the_conference(self, db, today):
        create_schedule(today + timedelta(days=30))
        assert is_it_debconf(None) == {"debconf_day": False, "debconf_soon": False}

    def test_the_day_before_the_conference(self, db, today):
        create_schedule(today + timedelta(days=1))
        assert is_it_debconf(None) == {"debconf_day": False, "debconf_soon": True}

    def test_the_day_of_the_conference(self, db, today):
        create_schedule(today)
        assert is_it_debconf(None) == {"debconf_day": True, "debconf_soon": False}
