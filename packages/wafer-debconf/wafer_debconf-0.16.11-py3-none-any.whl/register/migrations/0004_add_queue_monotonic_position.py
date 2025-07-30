from __future__ import unicode_literals

from itertools import count

from django.db import migrations, models


temp_counter = count()
def temp_count():
    return next(temp_counter)


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0003_remove_accomm_special_needs'),
    ]

    operations = [
        migrations.AddField(
            model_name='queueslot',
            name='monotonic_position',
            field=models.IntegerField(default=temp_count),
            preserve_default=False,
        ),
    ]
