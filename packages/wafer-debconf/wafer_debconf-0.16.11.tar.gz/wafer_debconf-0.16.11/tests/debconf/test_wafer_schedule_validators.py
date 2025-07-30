import debconf.models


class TestWaferScheduleValidators:
    def test_drop_non_contiguous(self):
        assert "non_contiguous" not in [x for _, x, _ in debconf.models.SCHEDULE_ITEM_VALIDATORS]
