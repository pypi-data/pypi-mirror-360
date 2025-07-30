import pytest


@pytest.mark.usefixtures("disable_caching")
class TestStatistics:
    def test_renders(self, client, create_talk, user, attendee):
        from wafer.talks.models import Review
        talk_1 = create_talk(status='A', username=attendee.user.username)
        talk_2 = create_talk(status='A')
        talk_3 = create_talk(status='A', username=attendee.user.username)
        Review.objects.create(talk=talk_2, reviewer=user, notes='Foo')
        response = client.get('/talks/statistics/')
        assert response.status_code == 200

        assert response.context['talks_submitted'] == 3
        assert response.context['talks_reviewed'] == 1
        assert response.context['talks_scheduled'] == 0
        assert response.context['hours_of_content'] == 0
        assert response.context['hours_of_concurrency'] == []
        assert response.context['talks_by_track'] == {}
        assert response.context['talks_by_type'] == {}
        assert response.context['speakers_by_country'] == [
            ('Canada', 1), ('Not registered yet', 1)]
