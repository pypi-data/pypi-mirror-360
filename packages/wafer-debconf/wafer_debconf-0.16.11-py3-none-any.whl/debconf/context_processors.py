import datetime
from django.conf import settings
from django.utils import timezone
from wafer.schedule.models import ScheduleBlock

def expose_settings(request):
    return {
        'TIME_ZONE': settings.TIME_ZONE,
        'DEBCONF_ONLINE': settings.DEBCONF_ONLINE,
        'WAFER_TALKS_OPEN': settings.WAFER_TALKS_OPEN,
        'RECONFIRMATION': settings.RECONFIRMATION,
        'SITE_DESCRIPTION': settings.SITE_DESCRIPTION,
        'SITE_AUTHOR': settings.SITE_AUTHOR,
        'USING_BADGES_APP': "badges" in settings.INSTALLED_APPS,
        'USING_FRONTDESK_APP': "front_desk" in settings.INSTALLED_APPS,
        'USING_REGISTER_APP': "register" in settings.INSTALLED_APPS,
        'USING_VOLUNTEERS_APP': "volunteers" in settings.INSTALLED_APPS,
        'USING_DAYTRIP': 'daytrip' in settings.PRICES,
    }


def is_it_debconf(request):
    today = timezone.now().date()
    two_days = datetime.timedelta(days=2)
    first = ScheduleBlock.objects.order_by('start_time').first()
    last = ScheduleBlock.objects.order_by('end_time').last()
    if not first or not last:
        return {}

    start = first.start_time.date()
    end =  last.end_time.date()
    return {
        'debconf_day': start <= today <= end,
        'debconf_soon': start - two_days <= today < start,
    }
