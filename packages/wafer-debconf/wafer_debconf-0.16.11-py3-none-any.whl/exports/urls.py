from django.urls import re_path

from exports.views import (
    AccommNightsExport, AttendeeAccommExport, AttendeeBadgeExport,
    BursaryExport, ChildCareExport, FingerprintExport, FoodExport,
    InvoiceExport, SecurityInfoExport, SpeakersRegistrationExport,
    SpecialDietExport, TalksExport, VisaExport,
)

urlpatterns = [
    re_path(r'^attendees/admin/export/accomm/$', AttendeeAccommExport.as_view(),
        name='attendee_admin_export_accomm'),
    re_path(r'^attendees/admin/export/accomm_nights/$', AccommNightsExport.as_view(),
        name='attendee_admin_export_accomm_nights'),
    re_path(r'^attendees/admin/export/badges/$', AttendeeBadgeExport.as_view(),
        name='attendee_admin_export_badges'),
    re_path(r'^attendees/admin/export/food/$', FoodExport.as_view(),
       name='attendee_admin_export_food'),
    re_path(r'^attendees/admin/export/special_diets/'
        r'(?P<date>[0-9-]+)/(?P<meal>[a-z]+)/$', SpecialDietExport.as_view()),
    re_path(r'^attendees/admin/export/child_care/$', ChildCareExport.as_view(),
        name='attendee_admin_export_childcare'),
    re_path(r'^attendees/admin/export/bursaries/$', BursaryExport.as_view(),
       name='attendee_admin_export_bursaries'),
    re_path(r'^talks/admin/export/$', TalksExport.as_view(),
        name='talks_admin_export'),
    re_path(r'^talks/admin/export/speakers-registration/$',
        SpeakersRegistrationExport.as_view(),
        name='talks_speakers_registration'),
    re_path(r'^attendees/admin/export/fingerprints/$', FingerprintExport.as_view(),
        name='attendee_admin_export_fingerprints'),
    re_path(r'^attendees/admin/export/invoices/$', InvoiceExport.as_view(),
        name='attendee_admin_export_invoices'),
    re_path(r'^attendees/admin/export/security-info/$', SecurityInfoExport.as_view(),
        name='attendee_admin_export_security_info'),
    re_path(r'^attendees/admin/export/visas/$', VisaExport.as_view(),
        name='attendee_admin_export_visas'),
]

exports = [
    {
        'url': u.name,
        'name': u.callback.view_class.name,
        'permission_required': u.callback.view_class.permission_required,
    }
    for u in urlpatterns if u.name
]
