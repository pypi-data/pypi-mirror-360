from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.db.models import Q
from django.template import Context, Template

from bursary.models import Bursary
from invoices.prices import invoice_user


SUBJECT = '{{ WAFER_CONFERENCE_NAME }}: Invoice Created'
TXT = '''Dear {{ name }},

We're sorry that we were unable to grant you food and/or accommodation
assistance for {{ WAFER_CONFERENCE_NAME }}.

We have now issued an invoice for your requested food and/or accommodation.
The invoice details are below.

If you still intend to attend the conference, please go to
<https://{{ WAFER_CONFERENCE_DOMAIN }}/accounts/profile/>
and pay the invoice directly online.

While we do accept cash payment on-site, we would strongly prefer if you
settled the invoice directly online.

If you wish to find your own food and accommodation, and attend the conference
itself without cost, please go to:
<https://{{ WAFER_CONFERENCE_DOMAIN }}/register/>
and update your registration to remove any food or accommodation that you are
being invoiced for.
Your invoice will be cancelled as part of the registration process.

If you no longer wish to attend {{ WAFER_CONFERENCE_NAME }}, please go to:
<https://{{ WAFER_CONFERENCE_DOMAIN }}/register/unregister>
and unregister.

Invoice number #{{ invoice_number }}

{{ invoice_details }}

Thanks for your interest in attending,

The {{ WAFER_CONFERENCE_NAME }} Registration Team
'''


class Command(BaseCommand):
    help = ("Issue invoices for attendees who applied for bursaries but "
            "didn't receive them")

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')
        parser.add_argument('--site', type=int, default=1,
                            help='Django site ID, default: 1')

    def badger(self, user, invoice, dry_run, site):
        to = user.email
        if dry_run:
            print('I would badger:', to)
            return
        context = Context({
            'invoice_number': invoice.reference_number,
            'invoice_details': invoice.text_details(),
            'name': user.userprofile.display_name(),
            'WAFER_CONFERENCE_DOMAIN': site.domain,
            'WAFER_CONFERENCE_NAME': site.name,
        })

        txt = Template(TXT).render(context)
        subject = Template(SUBJECT).render(context)
        email_message = EmailMultiAlternatives(subject, txt, to=[to])
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')
        site = Site.objects.get(id=1)
        for bursary in Bursary.objects.filter(
                Q(request_food=True,
                  food_status__in=('expired', 'denied', 'canceled'))
                | Q(request_accommodation=True,
                  accommodation_status__in=('expired', 'denied', 'canceled'))):
            user = bursary.user
            if not bursary.user.userprofile.is_registered():
                continue
            attendee = user.attendee
            if attendee.new_invoices.exists():
                continue
            if attendee.billable() and not attendee.paid():
                invoice = invoice_user(user, save=not dry_run)['invoice']
                self.badger(user, invoice, dry_run, site)
