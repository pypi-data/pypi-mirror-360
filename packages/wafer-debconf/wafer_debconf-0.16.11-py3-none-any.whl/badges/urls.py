from django.urls import re_path

from badges.views import OwnBadge, CheckInBadgeView

urlpatterns = [
    re_path(r'^$', OwnBadge.as_view(),
        name='badges.own'),
    re_path(r'^check_in/(?P<username>[\w.@+-]+)/$', CheckInBadgeView.as_view(),
        name='badges.check_in'),
]
