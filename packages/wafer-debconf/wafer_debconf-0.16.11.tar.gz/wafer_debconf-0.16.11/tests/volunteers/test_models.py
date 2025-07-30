from volunteers.models import Volunteer


class TestVolunteer:
    def test_basics(self, user, db):
        Volunteer.objects.create(user=user, staff_rating=Volunteer.RATINGS[-1][0])
