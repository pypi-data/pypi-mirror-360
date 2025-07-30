from django.core.management.base import BaseCommand
from django.db.models import F, Q
from functools import reduce
from random import shuffle
from datetime import timedelta


from wafer.talks.models import Talk, ACCEPTED
from wafer.schedule.models import Slot, Venue, ScheduleItem


def commaseparated(s):
    return s.split(",")


class Command(BaseCommand):
    help = "Schedule selected talks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--language",
            type=commaseparated,
            help="Select only talks from LANGUAGE (single language, or comma-separated)",
        )
        parser.add_argument(
            "--talk-type",
            action="append",
            help="Select only talks from the named talk type",
        )
        parser.add_argument("--limit", type=int, help="Schedule only LIMIT items")
        parser.add_argument("--start", help="when to start scheduling")
        parser.add_argument("--end", help="when to end scheduling")
        parser.add_argument("--duration", type=int, help="select only slots with duration of DURATION minutes")
        parser.add_argument("--venue", action="append", help="Schedule only to VENUE")
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Really schedule (otherwise just print what would have been done)",
        )

    def handle(self, *args, **options):
        talks = Talk.objects.filter(
            status=ACCEPTED, scheduleitem__isnull=True
        ).order_by("talk_id")
        if options["language"]:
            talks = talks.filter(language__in=options["language"])
        if options["talk_type"]:
            name_filters = [Q(talk_type__name__icontains=v) for v in options["talk_type"]]
            condition = reduce(lambda x, y: x | y, name_filters)
            talks = talks.filter(condition)

        valid_slots = []

        slots = Slot.objects.all()
        if options["start"]:
            slots = slots.filter(start_time__gte=options["start"])
        if options["end"]:
            slots = slots.filter(end_time__lte=options["end"])
        if options["duration"]:
            duration = timedelta(minutes=options["duration"])
            slots = [
                s for s in slots
                if s.end_time - s.start_time == duration
            ]

        venues = Venue.objects.all().filter(video=True).order_by("id")
        if options["venue"]:
            venues = venues.filter(name__icontains=options["venue"])

        for slot in slots:
            if ScheduleItem.objects.filter(slots=slot, expand=True).exists():
                continue
            for venue in venues:
                if ScheduleItem.objects.filter(slots=slot, venue=venue).exists():
                    continue
                valid_slots.append((slot, venue))

        shuffle(valid_slots)
        available_slots = iter(valid_slots)

        count = 0
        for talk in talks:
            try:
                slot, venue = next(available_slots)
            except StopIteration:
                print(f"W: no slot left to schedule \"{talk}\"")
                continue
            print(f"Scheduling \"{talk}\" to {slot} in {venue}")
            if options["yes"]:
                item = ScheduleItem.objects.create(
                    venue=venue,
                    talk=talk,
                )
                item.slots.add(slot)
            count += 1
            if options["limit"] and count >= options["limit"]:
                break
