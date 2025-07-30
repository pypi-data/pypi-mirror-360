from collections import Counter, OrderedDict, defaultdict

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from bakery.views import BuildableTemplateView

from bursary.models import Bursary, BURSARY_STATUS_CHOICES
from front_desk.models import CheckIn
from register.models import Attendee, Meal, user_is_registered


def clean_almostdicts(value):
    if not isinstance(value, dict):
        return value

    return OrderedDict(
        (k, clean_almostdicts(v)) for k, v in value.items()
    )


class StatisticsView(BuildableTemplateView):
    build_path = 'register/statistics/index.html'
    template_name = 'register/statistics.html'
    cache_key = 'register:statistics'
    cache_timeout = 30*60 if not settings.DEBUG else 10

    def get_context_data(self, **kwargs):
        from register.views import STEPS
        retval = cache.get(self.cache_key)
        if retval:
            return retval

        attendees = Attendee.objects.all()
        attendees_count = len(attendees)
        attendees_registered = 0
        attendees_approved = 0
        attendees_pending_approval = 0
        attendees_denied_approval = 0
        attendees_confirmed = 0
        attendees_arrived = 0
        attendees_by_country = defaultdict(Counter)
        attendees_by_language = defaultdict(Counter)
        attendees_by_gender = defaultdict(Counter)
        fees = defaultdict(Counter)
        tshirts = defaultdict(Counter)
        tshirts_total = Counter()
        shoes = defaultdict(Counter)
        shoes_total = Counter()
        accomm_total = 0
        accomm_confirmed = 0
        accommodation = defaultdict(Counter)
        food_total = 0
        food_confirmed = 0
        food_restrictions = defaultdict(Counter)
        food_restrictions['No restrictions']  # get that on top of the list
        meals = defaultdict(
            lambda: defaultdict(Counter)
        )
        for attendee in attendees:
            if attendee.completed_register_steps >= len(STEPS) - 1:
                attendees_registered += 1
            else:
                continue

            paid = attendee.paid()

            try:
                bursary = Bursary.objects.get(user=attendee.user)
            except Bursary.DoesNotExist:
                bursary = Bursary()

            approved = attendee.registration_approved()
            if approved:
                attendees_approved += 1
            elif bursary.attendance_status in ('submitted', 'ranked', 'pending'):
                attendees_pending_approval += 1
            elif bursary.attendance_status in ('denied', 'expired', 'canceled'):
                attendees_denied_approval += 1

            checked_in = CheckIn.objects.filter(attendee=attendee).exists()

            if checked_in:
                attendees_arrived += 1

            reconfirm = attendee.confirmed() and approved

            if reconfirm:
                attendees_confirmed += 1

            fees[attendee.fee]['all'] += 1
            if paid:
                fees[attendee.fee]['paid'] += 1

            if attendee.t_shirt_size:
                size = attendee.t_shirt_size
                tshirts[size]['all'] += 1
                tshirts_total['all'] += 1
                if reconfirm:
                    tshirts[size]['confirmed'] += 1
                    tshirts_total['confirmed'] += 1

            if attendee.shoe_size:
                size = attendee.shoe_size
                shoes[size]['all'] += 1
                shoes_total['all'] += 1
                if reconfirm:
                    shoes[size]['confirmed'] += 1
                    shoes_total['confirmed'] += 1

            attendees_by_country[attendee.country_name]['all'] += 1
            if reconfirm:
                attendees_by_country[attendee.country_name]['confirmed'] += 1

            attendees_by_gender[attendee.gender]['all'] += 1
            if reconfirm:
                attendees_by_gender[attendee.gender]['confirmed'] += 1

            languages = set(
                attendee.languages.lower()
                .replace(',', ' ')
                .replace('/', ' ')
                .replace(';', ' ')
                .split()
            )
            for language in languages:
                attendees_by_language[language]['all'] += 1
                if reconfirm:
                    attendees_by_language[language]['confirmed'] += 1

            try:
                accomm = attendee.accomm
                if not accomm.nights.exists():
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                pass
            else:
                accomm_total += 1
                if reconfirm:
                    accomm_confirmed += 1

                for night in attendee.accomm.nights.all():
                    accommodation[night]['all'] += 1
                    if reconfirm:
                        accommodation[night]['confirmed'] += 1

            try:
                food = attendee.food
                if not food.meals.exists():
                    raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                pass
            else:
                food_total += 1
                if reconfirm:
                    food_confirmed += 1

                markers = []
                if food.diet:
                    markers.append(food.diet.title())
                if not markers:
                    markers = ['No restrictions']

                food_restrictions[' '.join(markers)]['all'] += 1
                if reconfirm:
                    food_restrictions[' '.join(markers)]['confirmed'] += 1

                for meal in food.meals.all():
                    meals[meal.date][meal.meal]['all'] += 1
                    if reconfirm:
                        meals[meal.date][meal.meal]['confirmed'] += 1

        bursaries_by_status = defaultdict(Counter)
        bursaries_travel = Counter()
        for bursary in Bursary.objects.all():
            if not user_is_registered(bursary.user):
                continue
            for type in ('food', 'accommodation', 'travel', 'expenses'):
                if getattr(bursary, 'request_%s' % type):
                    status = getattr(bursary, '%s_status' % type)
                    bursaries_by_status[type]['all'] += 1
                    bursaries_by_status[type][status] += 1
                    if type == 'travel':
                        amount = bursary.travel_bursary
                        if amount is None:
                            continue
                        bursaries_travel['all'] += amount
                        bursaries_travel[status] += amount

        # Prepare for presentation
        fees = OrderedDict(
            (label, fees[key])
            for key, label in Attendee.FEES.items()
        )
        attendees_by_country = sorted(
            attendees_by_country.items(), key=lambda x: (-x[1]['all'], x[0])
        )
        attendees_by_gender = sorted(
            attendees_by_gender.items(), key=lambda x: (-x[1]['all'], x[0])
        )
        attendees_by_language = sorted(
            attendees_by_language.items(), key=lambda x: (-x[1]['all'], x[0])
        )
        tshirts = OrderedDict(
            (label, tshirts[key])
            for key, label in settings.DEBCONF_T_SHIRT_SIZES
            if key
        )
        shoes = OrderedDict(
            (size, shoes[size])
            for size, label in settings.DEBCONF_SHOE_SIZES
            if size
        )
        if not settings.DEBCONF_SHOE_SIZES:
            shoes = None
        accommodation = OrderedDict(
            sorted(
                (night.date, counts)
                for night, counts in accommodation.items()
            )
        )
        meal_labels = list(Meal.MEALS.values())
        meals = OrderedDict(
            (day, [day_meals[key] for key in Meal.MEALS])
            for day, day_meals in sorted(meals.items())
        )

        bursary_statuses = ['All'] + [
            choice[0].title() for choice in BURSARY_STATUS_CHOICES
        ]

        bursaries_by_status = OrderedDict(
            (type.title(), OrderedDict(
                (status.lower(), counter[status.lower()])
                for status in bursary_statuses
            ))
            for type, counter in bursaries_by_status.items()
        )
        bursaries_travel = OrderedDict(
            (status, bursaries_travel[status.lower()])
            for status in bursary_statuses
        )

        retval = clean_almostdicts({
            'DEBCONF_BURSARY_CURRENCY': settings.DEBCONF_BURSARY_CURRENCY,
            'DEBCONF_REVIEW_FREE_ATTENDEES':
                settings.DEBCONF_REVIEW_FREE_ATTENDEES,
            'attendees_count': attendees_count,
            'attendees_registered': attendees_registered,
            'attendees_approved': attendees_approved,
            'attendees_pending_approval': attendees_pending_approval,
            'attendees_denied_approval': attendees_denied_approval,
            'attendees_confirmed': attendees_confirmed,
            'attendees_arrived': attendees_arrived,
            'fees': fees,
            'tshirts': tshirts,
            'tshirts_total': tshirts_total,
            'shoes': shoes,
            'shoes_total': shoes_total,
            'attendees_by_country': attendees_by_country,
            'attendees_by_language': attendees_by_language,
            'attendees_by_gender': attendees_by_gender,
            'accomm_total': accomm_total,
            'accomm_confirmed': accomm_confirmed,
            'accommodation': accommodation,
            'food_total': food_total,
            'food_confirmed': food_confirmed,
            'food_restrictions': food_restrictions,
            'genders': Attendee.GENDERS,
            'meal_labels': meal_labels,
            'meals': meals,
            'bursary_statuses': bursary_statuses,
            'bursaries_by_status': bursaries_by_status,
            'bursaries_travel': bursaries_travel,
        })

        cache.set(self.cache_key, retval, self.cache_timeout)
        return retval
