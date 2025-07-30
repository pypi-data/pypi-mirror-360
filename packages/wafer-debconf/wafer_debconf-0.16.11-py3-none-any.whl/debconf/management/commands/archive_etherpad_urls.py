import re

from django.core.management.base import BaseCommand

from wafer.talks.models import TalkUrl


class Command(BaseCommand):
    help = "Update etherpad URLs to point to archived TXT versions"

    def add_arguments(self, parser):
        parser.add_argument('--talk', type=int,
            help='Act only on a specific talk ID. Default: all talks')
        parser.add_argument('urlbase', metavar='URL_BASE',
            help='Prefix pad URLs with the given base')
        parser.add_argument('--suffix', default='.txt',
            help='Suffix pad URLs with the given extension. Default: .txt')

    def handle(self, *args, **options):
        if options['talk']:
            urls = TalkUrl.objects.filter(talk_id=options['talk'])
        else:
            urls = TalkUrl.objects.all()

        urls = urls.filter(description='etherpad')

        for talkurl in urls:
            m = re.search(r'/p/([^/]*)$', talkurl.url)
            if not m:
                print("Unable to parse pad URL:", talkurl.url)
                continue
            pad = m.group(1)
            talkurl.url = options['urlbase'] + pad + options['suffix']
            talkurl.save()
