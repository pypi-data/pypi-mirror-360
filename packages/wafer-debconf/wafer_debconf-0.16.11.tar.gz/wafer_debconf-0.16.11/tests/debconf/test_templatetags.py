from collections import namedtuple
import pytest

from django.conf import settings

from debconf.templatetags.debconf import hls_stream_url
from debconf.templatetags.debconf import rtmp_stream_url
from debconf.templatetags.debconf import irc_channels


Venue = namedtuple("Venue", ["name"])


@pytest.fixture
def venue():
    return Venue(name="Room 1")


class TestHLSStreamURL:
    def test_fixed_url(self, monkeypatch, venue):
        monkeypatch.setattr(
            settings, "DEBCONF_VENUE_STREAM_HLS_URL", "https://foo.bar/stream.m3u8"
        )
        assert hls_stream_url(venue) == "https://foo.bar/stream.m3u8"

    def test_url_by_venue_name(self, monkeypatch, venue):
        monkeypatch.setattr(
            settings, "DEBCONF_VENUE_STREAM_HLS_URL", "https://foo.bar/{name}.m3u8"
        )
        assert hls_stream_url(venue) == "https://foo.bar/room-1.m3u8"


class TestRTMPStreamURL:
    def test_fixed_url(self, monkeypatch, venue):
        monkeypatch.setattr(
            settings, "DEBCONF_VENUE_STREAM_RTMP_URL", "rtmp://foo.bar/stream"
        )
        assert rtmp_stream_url(venue, "src") == "rtmp://foo.bar/stream"

    def test_url_by_venue_name(self, monkeypatch, venue):
        monkeypatch.setattr(
            settings,
            "DEBCONF_VENUE_STREAM_RTMP_URL",
            "rtmp://foo.bar/stream/{name}_{quality}",
        )
        assert rtmp_stream_url(venue, "src") == "rtmp://foo.bar/stream/room-1_src"


class TestIRCChannels:
    def test_fixed_channel(self, monkeypatch, venue):
        monkeypatch.setattr(settings, "DEBCONF_VENUE_IRC_CHANNELS", ["#debconf"])
        assert irc_channels(venue) == ["#debconf"]

    def test_room_channel_plus_general_channel(self, monkeypatch, venue):
        monkeypatch.setattr(
            settings, "DEBCONF_VENUE_IRC_CHANNELS", ["#myconf-{name}", "#myconf"]
        )
        assert irc_channels(venue) == ["#myconf-room-1", "#myconf"]
