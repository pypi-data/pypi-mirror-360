from django.urls import re_path

from daytrip.views import DayTripView, InsuranceView

urlpatterns = [
    re_path(r'^$', DayTripView.as_view(), name='day-trip'),
    re_path(r'^insurance/$', InsuranceView.as_view(), name='day-trip-insurance'),
]
