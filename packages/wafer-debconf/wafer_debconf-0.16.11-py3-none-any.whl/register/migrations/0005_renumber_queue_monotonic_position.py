from __future__ import unicode_literals

from itertools import count

from django.db import migrations


def renumber_slots(apps, schema_editor):
    Queue = apps.get_model('register', 'Queue')
    for queue in Queue.objects.all():
        counter = count()
        for slot in queue.slots.order_by('timestamp'):
            slot.monotonic_position = next(counter)
            slot.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0004_add_queue_monotonic_position'),
    ]

    operations = [
        migrations.RunPython(renumber_slots, noop),
    ]
