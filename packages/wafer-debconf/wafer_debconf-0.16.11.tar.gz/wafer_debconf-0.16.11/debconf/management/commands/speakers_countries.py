import sys


from django.contrib.sites.models import Site
from django.conf import settings
from django.core.management.base import BaseCommand


from register.models import Attendee
from wafer.talks.models import Talk
from wafer.talks.models import ACCEPTED


class Command(BaseCommand):
    help = "List country speakers for each talk."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        talks = Talk.objects.filter(
            status=ACCEPTED,
            scheduleitem=None,
        ).order_by(
            "title"
        ).prefetch_related(
            "authors",
        )
        site = Site.objects.first().domain
        for talk in talks:
            print(talk.title)
            print('-' * len(talk.title))
            print(f"Link: http://{site}{talk.get_absolute_url()}")
            for author in talk.authors.all():
                name = author.get_full_name() or author.username
                try:
                    country = author.attendee.country_name
                except Attendee.DoesNotExist:
                    country = "?"
                print(f"{name}: {country}")
            if talk.notes:
                print(f"Notes: {talk.notes}")
            print("")
            print("")

