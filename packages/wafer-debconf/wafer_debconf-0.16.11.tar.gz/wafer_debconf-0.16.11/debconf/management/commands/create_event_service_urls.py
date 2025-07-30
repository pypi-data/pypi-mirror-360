from django.core.management.base import BaseCommand

from wafer.talks.models import ACCEPTED, Talk
from debconf.talk_urls import create_online_service_urls


class Command(BaseCommand):
    help = "Generate online service (Jitsi, etherpad, etc.) URLs for events"

    def add_arguments(self, parser):
        parser.add_argument('--regenerate', action='store_true',
            help='Delete existing URLs and replace them')
        parser.add_argument('--talk', type=int,
            help='Act only on a specific talk ID. Default: all ACCEPTED talks')

    def handle(self, *args, **options):
        if options['talk']:
            talks = Talk.objects.filter(talk_id=options['talk'])
        else:
            talks = Talk.objects.filter(status=ACCEPTED)

        for talk in talks:
            create_online_service_urls(talk, options['regenerate'])
