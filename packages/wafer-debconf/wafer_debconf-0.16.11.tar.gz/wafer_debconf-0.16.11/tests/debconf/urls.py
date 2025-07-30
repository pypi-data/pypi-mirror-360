from django.conf.urls import include
from django.urls import re_path


urlpatterns = [
    re_path(r'^badges/', include('badges.urls')),
    re_path(r'^bursary/', include('bursary.urls')),
    re_path(r'^front_desk/', include('front_desk.urls')),
    re_path(r'^invoices/', include('invoices.urls')),
    re_path(r'^register/', include('register.urls')),

    re_path(r'', include('debconf.urls')),
    re_path(r'', include('exports.urls')),
    re_path(r'', include('wafer.urls')),
]
