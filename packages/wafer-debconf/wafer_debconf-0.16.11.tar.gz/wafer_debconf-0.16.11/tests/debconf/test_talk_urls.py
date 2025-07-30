import pytest

from wafer.talks.models import TalkUrl

from debconf.talk_urls import create_online_service_urls


@pytest.fixture(autouse=True)
def url_settings(settings):
    settings.DEBCONF_TALK_PROVISION_URLS = {
        "etherpad": {
            "pattern": "https://pad.online.debconf.org/p/{id}-{slug:.32}",
            "public": True,
        },
        "jitsi": {
            "pattern": "https://jitsi.debian.social/{id}-{slug}-{secret16}",
            "public": False,
        },
    }


def etherpad(talk):
    return TalkUrl.objects.get(talk=talk, description="etherpad")


def jitsi(talk):
    return TalkUrl.objects.get(talk=talk, description="jitsi")


class TestCreateOnlineServiceUrls:
    def test_id_and_slug(self, talk):
        create_online_service_urls(talk)
        assert (
            etherpad(talk).url
            == f"https://pad.online.debconf.org/p/{talk.pk}-hello-world"
        )

    def test_secret16(self, talk, mocker):
        mocker.patch(
            "debconf.talk_urls.get_random_string", return_value="01234567890abcdef"
        )
        create_online_service_urls(talk)
        assert (
            jitsi(talk).url
            == f"https://jitsi.debian.social/{talk.pk}-hello-world-01234567890abcdef"
        )

    def test_public(self, talk):
        create_online_service_urls(talk)
        assert etherpad(talk).public

    def test_private(self, talk):
        create_online_service_urls(talk)
        assert not jitsi(talk).public
