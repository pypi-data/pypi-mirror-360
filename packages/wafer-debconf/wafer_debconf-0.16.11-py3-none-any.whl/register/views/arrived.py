from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils.crypto import constant_time_compare
from django.utils import timezone
from django.views.generic import View
from register.models import Attendee
from front_desk.models import CheckIn


class DCScheduleArrived(View):
    def arrived_users(self):
        queryset = Attendee.objects.filter(announce_me=True).select_related(
            'user',
            'user__userprofile',
            'check_in',
        )
        now = timezone.now()
        for attendee in queryset:
            user = attendee.user
            try:
                arrived = attendee.check_in is not None
            except CheckIn.DoesNotExist:
                arrived = False

            departed = False
            if attendee.departure:
                departed = attendee.departure < now

            yield {
                'username': user.username,
                'arrived': arrived,
                'departed': departed,
                'name': user.userprofile.display_name(),
                'nick': attendee.nametag_3,
            }

    def get(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        auth = auth_header.split(None, 1)
        if not constant_time_compare(auth, ['Bearer', settings.DCSCHEDULE_TOKEN]):
            raise PermissionDenied('Missing/Invalid Authorization token')
        return JsonResponse({
            'arrived': list(self.arrived_users())
        })


