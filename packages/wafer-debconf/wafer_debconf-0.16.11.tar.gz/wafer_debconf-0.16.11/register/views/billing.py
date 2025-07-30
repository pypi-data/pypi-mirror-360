import json
import logging

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.utils import timezone

from bursary.models import Bursary
from invoices.prices import invoice_user
from register.forms.billing import BillingForm
from register.models import Attendee, Food
from register.models.accommodation import accomm_option_choices
from register.models.queue import Queue
from register.views.core import RegisterStep


class BillingView(RegisterStep):
    title = 'Billing'
    template_name = 'register/page/billing.html'
    form_class = BillingForm

    def get_initial(self):
        attendee = self.request.user.attendee
        initial = {
            'billing_address': attendee.billing_address,
            'invoiced_entity': attendee.invoiced_entity,
        }
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['attendee'] = self.request.user.attendee
        return kwargs

    def will_invoice(self):
        attendee = self.request.user.attendee
        if attendee.new_invoices.exists():
            return False
        if not attendee.billable():
            return False
        if attendee.paid():
            return False
        return True

    def will_reinvoice(self):
        user = self.request.user
        attendee = user.attendee
        if not attendee.new_invoices.exists():
            return False

        total = sum(invoice.total for invoice in attendee.new_invoices.all())

        invoice = invoice_user(user)
        return invoice['total'] != total and invoice['total'] > 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        attendee = user.attendee

        invoice = None
        will_reinvoice = self.will_reinvoice()
        if self.will_invoice() or will_reinvoice:
            invoice = invoice_user(user)

        context.update({
            'attendee': attendee,
            'will_reinvoice': will_reinvoice,
            'invoice': invoice,
            'DEBCONF_BILLING_CURRENCY': settings.DEBCONF_BILLING_CURRENCY,
            'DEBCONF_BILLING_CURRENCY_SYMBOL':
                settings.DEBCONF_BILLING_CURRENCY_SYMBOL,
            'DEBCONF_BURSARY_CURRENCY': settings.DEBCONF_BURSARY_CURRENCY,
            'DEBCONF_BURSARY_CURRENCY_SYMBOL':
                settings.DEBCONF_BURSARY_CURRENCY_SYMBOL,
            'DEBCONF_LOCAL_CURRENCY': settings.DEBCONF_LOCAL_CURRENCY,
            'DEBCONF_LOCAL_CURRENCY_SYMBOL':
                settings.DEBCONF_LOCAL_CURRENCY_SYMBOL,
        })
        return context

    def form_valid(self, form):
        from register.views import STEPS

        user = self.request.user
        data = form.cleaned_data

        user.attendee = Attendee.objects.update_or_create(
            user=user, defaults=data)[0]

        if self.will_reinvoice():
            user.attendee.new_invoices.update(status='canceled')
            invoice_user(user, save=True)
        elif self.will_invoice():
            invoice_user(user, save=True)

        for step in STEPS:
            step(request=self.request).registration_completed(user.attendee)

        return super().form_valid(form)

    def get_email_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        attendee = user.attendee

        try:
            bursary = user.bursary
        except Bursary.DoesNotExist:
            bursary = None

        try:
            food = user.attendee.food
        except ObjectDoesNotExist:
            food = None

        try:
            accomm = user.attendee.accomm
        except ObjectDoesNotExist:
            accomm = None

        try:
            child_care = user.attendee.child_care
        except ObjectDoesNotExist:
            child_care = None

        context = super().get_context_data(**kwargs)

        context.update({
            'accomm': accomm,
            'attendee': attendee,
            'bursary': bursary,
            'child_care': child_care,
            'food': food,
            'profile': user.userprofile,
            'user': user,
            'DEBCONF_BILLING_CURRENCY': settings.DEBCONF_BILLING_CURRENCY,
            'DEBCONF_BILLING_CURRENCY_SYMBOL':
                settings.DEBCONF_BILLING_CURRENCY_SYMBOL,
            'DEBCONF_BURSARY_CURRENCY': settings.DEBCONF_BURSARY_CURRENCY,
            'DEBCONF_BURSARY_CURRENCY_SYMBOL':
                settings.DEBCONF_BURSARY_CURRENCY_SYMBOL,
            'DEBCONF_CITY': settings.DEBCONF_CITY,
            'DEBCONF_COLLECT_AFFILIATION': settings.DEBCONF_COLLECT_AFFILIATION,
            'DEBCONF_DATES': settings.DEBCONF_DATES,
            'DEBCONF_LOCAL_CURRENCY': settings.DEBCONF_LOCAL_CURRENCY,
            'DEBCONF_LOCAL_CURRENCY_SYMBOL':
                settings.DEBCONF_LOCAL_CURRENCY_SYMBOL,
            'DEBCONF_REVIEW_FREE_ATTENDEES':
                settings.DEBCONF_REVIEW_FREE_ATTENDEES,
            'DEBCONF_SHOE_SIZES': settings.DEBCONF_SHOE_SIZES,
        })
        if accomm and accomm.option:
            context.update({
                'accomm_option': dict(accomm_option_choices())[accomm.option],
            })
        if attendee:
            context.update({
                'fee': Attendee.FEES[attendee.fee],
                'gender': Attendee.GENDERS[attendee.gender],
                't_shirt_size':
                    dict(settings.DEBCONF_T_SHIRT_SIZES)[attendee.t_shirt_size],
            })
        if bursary:
            context['bursary_need'] = Bursary.BURSARY_NEEDS.get(bursary.need)
        if food:
            context['diet'] = Food.DIETS[food.diet]

        return context

    def registration_completed(self, attendee):
        fresh_registration = False
        user = attendee.user
        if attendee.completed_register_steps <= self.register_step:
            fresh_registration = True
            attendee.completed_register_steps = self.register_step + 1
            attendee.completed_timestamp = timezone.now()
            attendee.save()

        queue = Queue.objects.get_or_create(name='Registration')[0]
        queue.slots.get_or_create(attendee=attendee)

        context = self.get_email_context_data()

        self.send_registered_email(user, context, fresh_registration)
        self.log_registration(user, context, fresh_registration)

    def send_registered_email(self, user, context, fresh_registration):
        txt = render_to_string('register/email_received.txt',
                               context, request=self.request)
        to = user.email
        site = get_current_site(self.request)
        if fresh_registration:
            status = 'received'
        else:
            status = 'updated'
        pending = ''
        if (settings.DEBCONF_REVIEW_FREE_ATTENDEES
                and not user.attendee.registration_approved()):
            pending = ' Pending'
        subject = f'[{site.name}]{pending} Registration {status}'
        email_message = EmailMultiAlternatives(subject, txt, to=[to])
        email_message.send()

    def log_registration(self, user, context, fresh_registration):
        log = logging.getLogger('register')
        data = {}
        m2m_links = {
            'accomm': ['nights'],
            'food': ['meals'],
        }
        m2m = {
            'attendee': ['addresses']
        }
        for model in ('accomm', 'attendee', 'bursary', 'child_care', 'food',
                      'profile', 'user'):
            if context[model]:
                data[model] = model_to_dict(context[model])
                for field in m2m_links.get(model, ()):
                    data[model][field] = [
                        linked.form_name for linked in data[model][field]
                    ]
                for field in m2m.get(model, ()):
                    data[model][field] = [
                        model_to_dict(obj)
                        for obj in getattr(context[model], field).all()
                    ]
            else:
                data[model] = {}
        data['user'].pop('password')

        log.info('User registered: user=%s updated=%s data=%s',
                 user.username, not fresh_registration,
                 json.dumps(data, cls=LogRegistrationJSONEncoder))


class LogRegistrationJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Model):
            return str(o)
        return super().default(o)
