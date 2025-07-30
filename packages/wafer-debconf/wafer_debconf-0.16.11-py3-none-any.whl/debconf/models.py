# We have no models, but some model-related behaviour

from collections import OrderedDict

from django.utils.translation import gettext_lazy as _
import debconf.talk_urls
from wafer.schedule.admin import SCHEDULE_ITEM_VALIDATORS

# Workaround strictness of wafer schedule validation
non_contiguous = None
for i, validator in enumerate(SCHEDULE_ITEM_VALIDATORS):
    __, err_type, __ = validator
    if err_type == "non_contiguous":
        non_contiguous = i
        break
if non_contiguous is not None:
    SCHEDULE_ITEM_VALIDATORS.pop(non_contiguous)

GENDERS = OrderedDict((
    ('', _('Decline to state')),
    ('m', _('Male')),
    ('f', _('Female')),
    ('n', _('Non-Binary')),
))
