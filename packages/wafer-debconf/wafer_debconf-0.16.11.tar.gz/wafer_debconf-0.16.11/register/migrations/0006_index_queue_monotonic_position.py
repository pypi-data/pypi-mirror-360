from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0005_renumber_queue_monotonic_position'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='queueslot',
            unique_together=set([('queue', 'monotonic_position')]),
        ),
    ]
