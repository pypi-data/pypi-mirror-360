from django.urls import re_path

from bursary.views import (
    AttendanceRequestReview,
    BursaryMassUpdate, BursaryRefereeAdd, BursaryRefereeExport,
    BursaryRequestExport, BursaryUpdate,
)

urlpatterns = [
    re_path(r'^admin/export/requests/$', BursaryRequestExport.as_view(),
        name='bursaries_admin_export_requests'),
    re_path(r'^admin/export/referees/$', BursaryRefereeExport.as_view(),
        name='bursaries_admin_export_referees'),
    re_path(r'^admin/add_referees/$', BursaryRefereeAdd.as_view(),
        name='bursaries_admin_add_referees'),
    re_path(r'^admin/update_requests/$', BursaryMassUpdate.as_view(),
        name='bursaries_admin_update_requests'),
    re_path(r'^admin/attendee-review/$', AttendanceRequestReview.as_view(),
        name='bursaries_admin_review_attendance'),
    re_path(r'^$', BursaryUpdate.as_view(), name='bursary_update'),
]
