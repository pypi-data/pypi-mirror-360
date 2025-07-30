from django.urls import re_path
from django.views.generic import RedirectView

from debconf.views import (
    ContentStatisticsView, DebConfScheduleView, IndexView,
    RobotsView, StatisticsView, now_or_next,
)

urlpatterns = [
    re_path(r'^favicon.ico$', RedirectView.as_view(url="/static/img/favicon.ico", permanent=True)),
    re_path(r'^schedule/$', DebConfScheduleView.as_view(),
        name='wafer_full_schedule'),
    re_path(r'^now_or_next/(?P<venue_id>\d+)/$', now_or_next, name="now_or_next"),
    re_path(r'^robots.txt$', RobotsView.as_view()),
    re_path(r'^$', IndexView.as_view()),
    re_path(r'^statistics/$', StatisticsView.as_view()),
    re_path(r'^talks/statistics/$', ContentStatisticsView.as_view(),
        name='content-statistics'),
]
