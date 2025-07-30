from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import Http404
from django.db import transaction
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView

from register.models.attendee import Attendee
from register.models.queue import Queue
from register.views import STEPS

from daytrip.forms import TravelInsuranceForm
from daytrip.models import TravelInsurance


class DayTripView(LoginRequiredMixin, TemplateView):
    template_name = 'daytrip/daytrip.html'

    def get_context_data(self, **kwargs):
        if 'daytrip' not in settings.PRICES:
            raise Http404
        user = self.request.user
        try:
            user.attendee
        except Attendee.DoesNotExist:
            raise PermissionDenied("Not yet registered")
        context = super().get_context_data(**kwargs)
        options = list(self.get_options())
        context['options'] = options
        context['registered_option'] = None
        context['invoice_register_step'] = f'register-step-{len(STEPS) - 2}'
        for option in options:
            if option['position']:
                context['registered_option'] = option
        context['DEBCONF_BILLING_CURRENCY_SYMBOL'] = (
            settings.DEBCONF_BILLING_CURRENCY_SYMBOL)
        context['DAYTRIP_OPEN'] = settings.DAYTRIP_OPEN
        context['DAYTRIP_INSURANCE_OPEN'] = settings.DAYTRIP_INSURANCE_OPEN
        return context

    def get_options(self):
        for key, option in settings.PRICES['daytrip'].items():
            queue = self.get_queue(key)
            attendees = [slot.attendee for slot in queue.slots.all()]
            slot = queue.slots.filter(attendee=self.request.user.attendee)
            position = None
            if slot.exists():
                position = slot.first().position
            yield {
                'id': key,
                'description': option['description'],
                'long_description': option['long_description'],
                'details_pdf': option.get('details_pdf'),
                'price': option['price'],
                'closed': option.get('closed', False),
                'insurance_price': option['insurance_price'],
                'position': position,
                'capacity': option['capacity'],
                'total_registered': len(attendees),
                'attendees': attendees,
            }

    def get_queue(self, key):
        return Queue.objects.get_or_create(name=f'DayTrip {key}')[0]

    def register(self, key, attendee):
        self.get_queue(key).slots.get_or_create(attendee=attendee)

    def unregister(self, key, attendee):
        self.get_queue(key).slots.filter(attendee=attendee).delete()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if not settings.DAYTRIP_OPEN:
            raise BadRequest("Registration is closed")
        try:
            daytrip = request.POST['daytrip']
            action = request.POST['action']
        except KeyError as e:
            raise BadRequest(e)
        try:
            attendee = request.user.attendee
        except Attendee.DoesNotExist:
            raise PermissionDenied("Not yet registered")
        if daytrip not in settings.PRICES['daytrip']:
            raise BadRequest("Unknown daytrip")
        if settings.PRICES['daytrip'][daytrip].get('closed', False):
            raise BadRequest("Daytrip registration is closed")
        if action == 'register':
            # Ensure we aren't double-registered
            for key in settings.PRICES['daytrip']:
                if key != daytrip:
                    self.unregister(key, attendee)
            self.register(daytrip, attendee)
        elif request.POST['action'] == 'unregister':
            self.unregister(daytrip, attendee)
        else:
            raise BadRequest("Unknown action")
        return self.get(request, *args, **kwargs)


class InsuranceView(UpdateView):
    form_class = TravelInsuranceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['DAYTRIP_INSURANCE_OPEN'] = settings.DAYTRIP_INSURANCE_OPEN
        return context

    def get_object(self, queryset=None):
        if 'daytrip' not in settings.PRICES:
            raise Http404
        attendee = self.request.user.attendee
        daytrip_option = attendee.daytrip_option
        if 'insurance_price' not in settings.PRICES['daytrip'][daytrip_option]:
            raise Http404
        try:
            return attendee.travel_insurance
        except TravelInsurance.DoesNotExist:
            return TravelInsurance(attendee=self.request.user.attendee)

    def post(self, request, *args, **kwargs):
        if not settings.DAYTRIP_INSURANCE_OPEN:
            raise BadRequest("Registration is closed")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('day-trip')
