from wafer.schedule.models import Slot
from debconf.views import get_current_slot
from datetime import timedelta


class TestGetCurrentSlot:
    def test_explicit_start_time(self, db, now):
        slot = Slot.objects.create(
            start_time=now - timedelta(minutes=30), end_time=now + timedelta(minutes=30)
        )
        assert get_current_slot() == slot

    def test_start_time_from_previous_slot(self, db, now):
        previous = Slot.objects.create(
            start_time=now - timedelta(hours=1), end_time=now
        )
        current = Slot.objects.create(
            previous_slot=previous, end_time=now + timedelta(hours=1)
        )
        assert get_current_slot() == current
