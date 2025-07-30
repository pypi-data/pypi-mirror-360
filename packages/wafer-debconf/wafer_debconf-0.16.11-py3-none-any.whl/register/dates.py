import datetime

from django.conf import settings

ARRIVE_ON_OR_AFTER = settings.DEBCONF_DATES[0][1]
ORGA_ARRIVE_ON_OR_AFTER = ARRIVE_ON_OR_AFTER
if settings.DEBCONF_ORGA_EARLY_DAYS:
    ORGA_ARRIVE_ON_OR_AFTER -= datetime.timedelta(days=settings.DEBCONF_ORGA_EARLY_DAYS)
LEAVE_ON_OR_BEFORE = settings.DEBCONF_DATES[-1][2]
if settings.DEBCONF_DEPARTURE_DAY:
    LEAVE_ON_OR_BEFORE += datetime.timedelta(days=1)
if settings.DEBCONF_TSHIRT_SWAP_ON_OR_AFTER:
    T_SHIRT_SWAP_ON_OR_AFTER = settings.DEBCONF_TSHIRT_SWAP_ON_OR_AFTER
else:
    T_SHIRT_SWAP_ON_OR_AFTER = LEAVE_ON_OR_BEFORE - datetime.timedelta(days=4)


def meals(orga=False):
    day = ARRIVE_ON_OR_AFTER
    while day <= LEAVE_ON_OR_BEFORE:
        if day in settings.DEBCONF_BRUNCHES:
            yield ('brunch', day)
        else:
            if settings.DEBCONF_BREAKFAST:
                yield ('breakfast', day)
            yield ('lunch', day)
        yield ('dinner', day)
        day += datetime.timedelta(days=1)


def nights(orga=False):
    day = ARRIVE_ON_OR_AFTER
    if orga:
        day = ORGA_ARRIVE_ON_OR_AFTER
    while day < LEAVE_ON_OR_BEFORE:
        yield day
        day += datetime.timedelta(days=1)


def parse_date(date):
    return datetime.date(*(int(part) for part in date.split('-')))


def meal_choices(orga=False):
    for meal, date in meals(orga=orga):
        date = date.isoformat()
        yield ('{}_{}'.format(meal, date),
               '{} {}'.format(meal.title(), date))


def conference_dinner_meal():
    date = settings.DEBCONF_CONFERENCE_DINNER_DAY
    if not date:
        return None
    return 'dinner_{}'.format(date.isoformat())


def skipped_meals():
    for meal, date in getattr(settings, 'DEBCONF_SKIPPED_MEALS', ()):
        yield f'{meal}_{date.isoformat()}'


def night_choices(orga=False):
    for date in nights(orga=orga):
        date = date.isoformat()
        yield ('night_{}'.format(date), 'Night of {}'.format(date))


def get_ranges_for_dates(dates):
    """Get ranges of consecutive dates for the given set of dates"""
    one = datetime.timedelta(days=1)

    ranges = []

    range_start = None
    range_end = None
    for date in sorted(dates):
        if range_start is None:
            range_start = date
        else:
            if date != range_end + one:
                # dates not consecutive, save old range and start new one
                ranges.append([range_start, range_end])
                range_start = date

        range_end = date

    ranges.append([range_start, range_end])
    return ranges
