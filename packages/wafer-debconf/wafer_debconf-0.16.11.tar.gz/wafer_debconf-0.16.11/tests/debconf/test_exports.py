from exports.views import VisaExport
from register.models import Visa


class FakeWriter:
    """Like a CSV DictWriter, for tests"""
    def __init__(self):
        self.rows = []

    def writerow(self, data):
        self.rows.append(data)


def get_exported_data(cbv):
    instance = cbv()
    object_list = instance.get_queryset()
    context = instance.get_context_data(object_list=object_list)
    writer = FakeWriter()
    instance.write_rows(writer, context['object_list'])
    return [dict(zip(instance.columns, row)) for row in writer.rows]


def test_visa_export_empty(attendee):
    data = get_exported_data(VisaExport)
    assert data == []


def test_visa_export_no_bursary(attendee):
    Visa.objects.create(attendee=attendee, country='TT')
    data = get_exported_data(VisaExport)
    assert data == [{
        'attendee.user.username': attendee.user.username,
        'attendee.user.userprofile.display_name':
            attendee.user.userprofile.display_name(),
        'attendee.user.email': attendee.user.email,
        'country': 'TT',
        'travel_bursary_status': '',
        'accommodation_bursary_status': '',
        'food_bursary_status': '',
        'attendance_approval_status': '',
    }]


def test_visa_export_submitted_bursary(bursary):
    attendee = bursary.user.attendee
    Visa.objects.create(attendee=attendee, country='TT')
    data = get_exported_data(VisaExport)
    assert data == [{
        'attendee.user.username': attendee.user.username,
        'attendee.user.userprofile.display_name':
            attendee.user.userprofile.display_name(),
        'attendee.user.email': attendee.user.email,
        'country': 'TT',
        'travel_bursary_status': 'submitted',
        'accommodation_bursary_status': 'submitted',
        'food_bursary_status': 'submitted',
        'attendance_approval_status': 'submitted',
    }]
