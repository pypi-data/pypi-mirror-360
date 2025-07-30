from register.models import Attendee
from wafer.schedule.admin import register_schedule_item_validator
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as N_


def validate_speaker_stay(all_items):
    errors = []
    for item in all_items:
        if not item.talk:
            continue
        for speaker in item.talk.authors.all():
            try:
                attendee = speaker.attendee
            except Attendee.DoesNotExist:
                continue
            for slot in item.slots.all():
                arrival = attendee.arrival
                if arrival and slot.get_start_time() < arrival:
                    errors.append(
                        _('<%(talk)s> scheduled %(scheduled)s; %(speaker)s arrives %(arrival)s') % {
                            'talk': item.talk.title,
                            'speaker': speaker.get_full_name(),
                            'scheduled': slot.get_start_time(),
                            'arrival': arrival,
                        }
                    )
                    break
                departure = attendee.departure
                if departure and slot.end_time > departure:
                    errors.append(
                        _('<%(talk)s> scheduled for %(scheduled)s; %(speaker)s departs %(departure)s') % {
                            'talk': item.talk.title,
                            'speaker': speaker.get_full_name(),
                            'scheduled': slot.end_time,
                            'departure': departure,
                        }
                    )
                    break
    return errors


register_schedule_item_validator(
    validate_speaker_stay,
    'speaker_not_at_conference',
    N_('Talk scheduled when speaker is not at the conference')
)
