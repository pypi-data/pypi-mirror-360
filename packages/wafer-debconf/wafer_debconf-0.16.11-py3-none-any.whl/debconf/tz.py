from datetime import datetime, timedelta

from django.utils.timezone import get_fixed_timezone, make_aware

AoE = get_fixed_timezone(timedelta(hours=-12))


def aoe_datetime(deadline_date):
    """Given a date() object, return a timezone-aware datetime() object,
    representing the end of day, anywhere on earth (AoE).
    """
    dt = datetime(deadline_date.year, deadline_date.month, deadline_date.day)
    dt += timedelta(days=1)  # midnight at the end of day
    return make_aware(dt, AoE)
