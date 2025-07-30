from datetime import timedelta


def get_start_end_for_scheduleitem(si):
    if not si.slots.exists():
        raise ValueError('M2M not realized yet, come back later')
    start = si.get_start_datetime()
    end = start + timedelta(minutes=si.get_duration_minutes())
    return (start, end)
