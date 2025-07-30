from django.core.management.base import BaseCommand

from register.models.attendee import Attendee
from register.models.queue import Queue


class Command(BaseCommand):
    help = ('Flush the PGP Keysigning queue and re-create, in sorted order. '
            'This lets us create a mostly-sorted list, at a freeze point.')

    def handle(self, *args, **options):
        queue = Queue.objects.get_or_create(name='PGP Keysigning')[0]
        queue.slots.all().delete()
        players = Attendee.objects.exclude(pgp_fingerprints='')
        players = players.order_by( 'user__first_name', 'user__last_name')
        for attendee in players:
            queue.slots.get_or_create(attendee=attendee)
