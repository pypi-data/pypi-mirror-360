from django.core.management.base import BaseCommand
from django.conf import settings

from register.dates import nights, meals
from register.models import AccommNight, Meal


class Command(BaseCommand):
    help = 'Create Meal and Night objects in the DB'

    def handle(self, *args, **options):
        for night in nights(orga=True):
            AccommNight.objects.get_or_create(date=night)
        skipped_meals = set(
            (meal, date)
            for (meal, date) in getattr(settings, 'DEBCONF_SKIPPED_MEALS', ())
        )
        for meal, date in meals(orga=True):
            if (meal, date) not in skipped_meals:
                Meal.objects.get_or_create(meal=meal, date=date)
