from datetime import time
import os
from wafer.settings import *

INSTALLED_APPS = (
    'django_countries',
    'compressor',
    'debconf.themes.empty',
) + INSTALLED_APPS

try:
    import django_extensions
    INSTALLED_APPS += ('django_extensions',)
except ImportError:
    pass

ALLOWED_HOSTS = ["*"]

TEMPLATES[0]['OPTIONS']['context_processors'] += (
    'debconf.context_processors.expose_settings',
    'debconf.context_processors.is_it_debconf',
)

BAKERY_VIEWS += (
    'debconf.views.RobotsView',
    'debconf.views.IndexView',
    'debconf.views.DebConfScheduleView',
    'debconf.views.StatisticsView',
    'debconf.views.ContentStatisticsView',
)

SANDBOX = False
DEBCONF_ONLINE = False
DEBCONF_DEPARTURE_DAY = True
DEBCONF_DEPARTURE_TIME = time(10)
DEBCONF_BREAKFAST = True
DEBCONF_BRUNCHES = []
DEBCONF_ORGA_EARLY_DAYS = 3
DEBCONF_TSHIRT_SWAP_ON_OR_AFTER = None
DEBCONF_BILLING_CURRENCY = 'USD'
DEBCONF_BILLING_CURRENCY_SYMBOL = '$'
DEBCONF_BURSARY_CURRENCY = 'USD'
DEBCONF_BURSARY_CURRENCY_SYMBOL = '$'
DEBCONF_LOCAL_CURRENCY = 'USD'
DEBCONF_LOCAL_CURRENCY_SYMBOL = '$'
DEBCONF_LIMITED_BURSARIES = False
DEBCONF_BURSARY_BUDGETS = {
    'general': {
        'description': 'Debian Contributor Bursary',
        'required_fields': ['reason_contribution', 'reason_plans'],
    },
    'diversity': {
        'description': 'Debian Diversity Bursary (newcomers to DebConf)',
        'required_fields': ['reason_diversity', 'reason_plans'],
    },
    'both': {
        'description': 'Debian Contributor and Diversity (considered for both)',
        'required_fields': ['reason_contribution', 'reason_diversity', 'reason_plans'],
    },
    'speaker': {
        'description': 'Invited Speaker',
        'permissions': ['bursary.invited_speaker'],
    },
    'dc-ctte': {
        'description': 'DebConf Committee (budgeted team travel)',
        'permissions': ['bursary.orga_travel'],
    },
    'dc-reg': {
        'description': 'DebConf Registration Team (budgeted team travel)',
        'permissions': ['bursary.orga_travel'],
    },
    'dc-video': {
        'description': 'DebConf Video Team (budgeted team travel)',
        'permissions': ['bursary.orga_travel'],
    },
}

DEBCONF_SECURITY_INFO = False

markdown_kwargs = {
    'extensions': [
        'markdown.extensions.smarty',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'mdx_linkify.mdx_linkify',
        'mdx_staticfiles',
    ],
    'output_format': 'html5',
}
MARKITUP_FILTER = ('wafer.markdown.bleached_markdown', markdown_kwargs)
WAFER_PAGE_MARKITUP_FILTER = ('markdown.markdown', markdown_kwargs)
MARKITUP_SET = 'markitup/sets/markdown/'
JQUERY_URL = 'vendor/jquery/jquery.js'

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

STATICFILES_FINDERS = (
    'compressor.finders.CompressorFinder',
) + STATICFILES_FINDERS

SITE_DESCRIPTION = os.getenv("SITE_DESCRIPTION")
SITE_AUTHOR = os.getenv("SITE_AUTHOR")

WAFER_SSO = ('gitlab',)
WAFER_GITLAB_HOSTNAME = 'salsa.debian.org'
WAFER_GITLAB_CLIENT_ID = os.getenv('WAFER_GITLAB_CLIENT_ID')
WAFER_GITLAB_CLIENT_SECRET = os.getenv('WAFER_GITLAB_CLIENT_SECRET')

WAFER_VIDEO_REVIEWER = False

DEBCONF_VENUE_STREAM_HLS_URL = "https://onsite.live.debconf.org/redir/live/main.m3u8"
DEBCONF_VENUE_STREAM_RTMP_URL = "rtmp://onsite.live.debconf.org/redir/front/main_{quality}"
DEBCONF_VENUE_IRC_CHANNELS = ["#debconf"]

WAFER_PUBLIC_ATTENDEE_LIST = False
