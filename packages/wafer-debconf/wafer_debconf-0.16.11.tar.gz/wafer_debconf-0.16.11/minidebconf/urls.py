from django.conf.urls import include
from django.urls import re_path
from minidebconf.views import RegisterView, UnregisterView, RegistrationFinishedView

urlpatterns = [
    re_path(r'^register/$', RegisterView.as_view(), name='register'),
    re_path(r'^unregister/$', UnregisterView.as_view(), name='unregister'),
    re_path(r'^register/finished/$', RegistrationFinishedView.as_view(), name='registration_finished'),
    re_path(r'', include('debconf.urls')),
    re_path(r'', include('wafer.urls')),
]
