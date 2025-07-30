from django.conf import settings
from django.db import migrations, models

from pytz import common_timezones


def tz_choices():
    """Duplicate logic from model, so that django doesn't constantly think
    choices has changed
    """
    timezones = common_timezones
    if settings.TIME_ZONE not in timezones:
        timezones.insert(0, settings.TIME_ZONE)
    return [(tz, tz) for tz in timezones]


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0003_fk_on_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteer',
            name='timezone',
            field=models.TextField(default='Etc/UTC', max_length=32,
                                   choices=tz_choices()),
        ),
    ]
