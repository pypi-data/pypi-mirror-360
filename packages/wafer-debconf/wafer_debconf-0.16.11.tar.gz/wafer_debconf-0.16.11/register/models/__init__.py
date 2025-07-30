from register.models.accommodation import Accomm, AccommNight
from register.models.address import Address
from register.models.attendee import Attendee
from register.models.childcare import ChildCare
from register.models.food import Food, Meal
from register.models.queue import Queue, QueueSlot
from register.models.visa import Visa
import register.speaker_stay

def user_is_registered(user):
    from register.views import STEPS
    last_step = len(STEPS) - 1
    return Attendee.objects.filter(
        user=user, completed_register_steps=last_step).exists()
