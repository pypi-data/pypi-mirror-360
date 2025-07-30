import re
from django import template
from django.conf import settings

from debconf.talk_urls import provision_urls_setting

register = template.Library()

debconf = {
    'BILLING_CURRENCY': settings.DEBCONF_BILLING_CURRENCY,
    'BILLING_CURRENCY_SYMBOL': settings.DEBCONF_BILLING_CURRENCY_SYMBOL,
    'BURSARY_CURRENCY': settings.DEBCONF_BURSARY_CURRENCY,
    'BURSARY_CURRENCY_SYMBOL': settings.DEBCONF_BURSARY_CURRENCY_SYMBOL,
    'LOCAL_CURRENCY': settings.DEBCONF_LOCAL_CURRENCY,
    'LOCAL_CURRENCY_SYMBOL': settings.DEBCONF_LOCAL_CURRENCY_SYMBOL,
}

@register.simple_tag
def debconf_setting(key):
    return debconf[key]


# These colors were taken by picking the lightest colors from
# https://en.wikipedia.org/wiki/Web_colors#X11_color_names then shuffling the
# list
colors = [
    ('#FFE4E1', 'MistyRose'),
    ('#F0FFF0', 'Honeydew'),
    ('#00FFFF', 'Cyan'),
    ('#E0FFFF', 'LightCyan'),
    ('#00FF00', 'Lime'),
    ('#D2B48C', 'Tan'),
    ('#FFD700', 'Gold'),
    ('#D3D3D3', 'LightGray'),
    ('#B0C4DE', 'LightSteelBlue'),
    ('#E6E6FA', 'Lavender'),
    ('#00BFFF', 'DeepSkyBlue'),
    ('#F5DEB3', 'Wheat'),
    ('#90EE90', 'LightGreen'),
    ('#FFB6C1', 'LightPink'),
    ('#FFA07A', 'LightSalmon'),
    ('#AFEEEE', 'PaleTurquoise'),
    ('#DDA0DD', 'Plum'),
    ('#FFFFE0', 'LightYellow'),
    ('#F0E68C', 'Khaki'),
]


@register.simple_tag
def debconf_track_color(track):
    if track:
        return colors[track.id % len(colors)][0]


@register.simple_tag
def is_among_authors(user, talk):
    return talk._is_among_authors(user)


@register.simple_tag
def talk_has_private_urls(talk):
    return talk.urls.filter(public=False).exists()


def venue_name(venue):
    return re.sub(r"[^a-z0-9-]+", "-", venue.name.lower())

@register.simple_tag
def hls_stream_url(venue):
    url = settings.DEBCONF_VENUE_STREAM_HLS_URL
    return url.format(name=venue_name(venue))

@register.simple_tag
def rtmp_stream_url(venue, quality):
    url = settings.DEBCONF_VENUE_STREAM_RTMP_URL
    return url.format(name=venue_name(venue), quality=quality)


@register.simple_tag
def irc_channels(venue):
    return [
        ch.format(name=venue_name(venue)) for ch in settings.DEBCONF_VENUE_IRC_CHANNELS
    ]
