from collections import defaultdict
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone

from debconf.models import GENDERS
from bakery.views import BuildableTemplateView
from wafer.talks.models import Talk, TalkType, Track
from wafer.schedule.views import ScheduleView
from wafer.schedule.models import Venue, ScheduleItem, Slot
from wafer.pages.models import Page


class RobotsView(BuildableTemplateView):
    build_path = 'robots.txt'
    template_name = 'debconf/robots.txt'
    content_type = 'text/plain; charset=UTF-8'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SANDBOX'] = settings.SANDBOX
        return context


class DebConfScheduleView(ScheduleView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracks'] = Track.objects.all()
        return context


def get_current_slot():
    now = timezone.now()

    for slot in Slot.objects.all():
        start = slot.get_start_time()
        end = slot.end_time
        if start <= now and now < end:
            return slot


class IndexView(BuildableTemplateView):
    build_path = 'index.html'
    template_name = 'wafer/index.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)

        venues = Venue.objects.filter(video=True)

        venue_blocks = [{'venue': venue} for venue in venues]

        current_slot = get_current_slot()
        if current_slot:
            events = ScheduleItem.objects.filter(slots=current_slot)
            for event in events:
                for blk in venue_blocks:
                    if event.venue == blk['venue']:
                        slots = list(event.slots.all())
                        blk['event'] = event
                        blk['start_time'] = slots[0].get_formatted_start_time()
                        blk['end_time'] = slots[-1].get_formatted_end_time()

        context_data['venue_blocks'] = venue_blocks

        try:
            context_data['page'] = Page.objects.get(slug="index", parent=None)
        except Page.DoesNotExist:
            pass

        return context_data


class StatisticsView(BuildableTemplateView):
    build_path = 'statistics/index.html'
    template_name = 'debconf/statistics.html'


class ContentStatisticsView(BuildableTemplateView):
    build_path = 'talks/statistics/index.html'
    template_name = 'debconf/content_statistics.html'
    cache_key = 'debconf:content_statistics'
    cache_timeout = 30*60 if not settings.DEBUG else 10

    def get_context_data(self, **kwargs):
        retval = cache.get(self.cache_key)
        if retval:
            return retval

        talks_submitted = Talk.objects.count()
        talks_reviewed = Talk.objects.filter(
            reviews__isnull=False).distinct().count()
        talks_scheduled = Talk.objects.filter(
            scheduleitem__isnull=False).distinct().count()

        minutes_of_content = 0
        for si in ScheduleItem.objects.filter(talk__isnull=False):
            duration = si.get_duration()
            minutes_of_content += duration['minutes'] + duration['hours'] * 60
        hours_of_content = minutes_of_content / 60

        concurrency_by_hour = defaultdict(int)
        for slot in Slot.objects.all():
            hour = slot.get_start_time().replace(
                minute=0, second=0, microsecond=0)
            concurrency_by_hour[hour] = max(concurrency_by_hour[hour],
                                            slot.scheduleitem_set.count())

        hours_of_concurrency = []
        if concurrency_by_hour:
            hours_of_concurrency = [
                (concurrency, sum(
                    1 for hour, hour_concurrency in concurrency_by_hour.items()
                    if hour_concurrency == concurrency))
                for concurrency in range(max(concurrency_by_hour.values()) + 1)]

        talks_by_track = {}
        for track in Track.objects.all():
            talks_by_track[track.name] = {
                'submitted': track.talk_set.count(),
                'scheduled': track.talk_set.filter(
                    scheduleitem__isnull=False).count(),
            }

        talks_by_type = {}
        for type_ in TalkType.objects.all():
            talks_by_type[type_.name] = {
                'submitted': type_.talk_set.count(),
                'scheduled': type_.talk_set.filter(
                    scheduleitem__isnull=False).count(),
            }

        countries = {}
        authors = set()
        for talk in Talk.objects.filter(status__in=('A', 'P')).prefetch_related('authors'):
            for author in talk.authors.all():
                if author.id in authors:
                    continue
                authors.add(author.id)
                try:
                    if (settings.WAFER_USER_IS_REGISTERED
                            == 'register.models.user_is_registered'):
                        country = author.attendee.country_name
                    elif (settings.WAFER_USER_IS_REGISTERED
                            == 'minidebconf.models.is_registered'):
                        country = author.registration.country.name
                    else:
                        country = 'Unknown'
                except ObjectDoesNotExist:
                    country = 'Not registered yet'
                countries.setdefault(country, 0)
                countries[country] += 1
        speakers_by_country = sorted(countries.items(), key=lambda i: -i[1])

        genders = {}
        User = get_user_model()
        for user in User.objects.filter(talks__status='A'):
            try:
                gender = user.attendee.gender
            except ObjectDoesNotExist:
                continue
            genders.setdefault(gender, 0)
            genders[gender] += 1
        speakers_by_gender = [(GENDERS[gender], count)
            for (gender, count) in genders.items()]
        speakers_by_gender.sort(key=lambda i: -i[1])


        retval = {
            'talks_submitted': talks_submitted,
            'talks_reviewed': talks_reviewed,
            'talks_scheduled': talks_scheduled,
            'hours_of_content': hours_of_content,
            'hours_of_concurrency': hours_of_concurrency,
            'talks_by_track': talks_by_track,
            'talks_by_type': talks_by_type,
            'speakers_by_country': speakers_by_country,
            'speakers_by_gender': speakers_by_gender,
        }

        cache.set(self.cache_key, retval, self.cache_timeout)
        return retval


def now_or_next(request, venue_id):
    talk_now = False
    talk_next = False
    reload_seconds = 60
    talk = None

    now = timezone.now()
    # now
    try:
        item = ScheduleItem.objects.filter(
            venue=venue_id,
            talk__isnull=False,
            slots__start_time__lte=now,
            slots__end_time__gte=now,
        ).order_by("slots__start_time")[0]
        duration = item.get_duration_minutes()
        end = item.get_start_datetime() + timedelta(minutes=duration)
        reload_seconds = (end - timezone.now()).total_seconds()

        talk_now = True
        talk = item.talk_id
    except IndexError:
        pass

    if not talk:
        # next
        try:
            item = ScheduleItem.objects.filter(
                venue=venue_id,
                talk__isnull=False,
                slots__start_time__gte=now
            ).order_by("slots__start_time")[0]
            reload_seconds = (item.get_start_datetime() - timezone.now()).total_seconds()
            talk_next = True
            talk = item.talk_id
        except IndexError:
            pass

    return JsonResponse({
        "now": talk_now,
        "next": talk_next,
        "reload_seconds": reload_seconds,
        "talk": talk,
    })
