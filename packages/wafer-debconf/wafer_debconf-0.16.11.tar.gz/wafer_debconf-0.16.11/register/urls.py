from django.urls import re_path
from django.views.generic.base import RedirectView

from register.views import STEPS
from register.views.arrived import DCScheduleArrived
from register.views.core import ClosedView, UnRegisterView
from register.views.statistics import StatisticsView


urlpatterns = [
    re_path(r'^$', RedirectView.as_view(url='step-0'), name='register'),
    re_path(r'^unregister$', UnRegisterView.as_view(), name='unregister'),
    re_path(r'^closed$', ClosedView.as_view(), name='register-closed'),
    re_path(r'^statistics/$', StatisticsView.as_view(), name='register-statistics'),
    re_path(r'^attendees/admin/export/arrived/$', DCScheduleArrived.as_view()),
]

for i, step in enumerate(STEPS):
    urlpatterns.append(
        re_path(r'^step-{}$'.format(i), step.as_view(),
            name='register-step-{}'.format(i)))
