from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.template import Context, Template

from register.models import Attendee


SUBJECT = '{{ WAFER_CONFERENCE_NAME }}: Invoice Cancelled'
TXT = '''Dear {{ name }},

Sorry, we see you had an outstanding invoice that doesn't apply any more
(due to a bursary or other change).

We have cancelled it.

Apologies for hassling about paying it.

Invoice number #{{ invoice_number }}

See you soon in {{ DEBCONF_CITY }},

The {{ WAFER_CONFERENCE_NAME }} Registration Team
'''


class Command(BaseCommand):
    help = ("Cancel invoices for attendees who got bursaries")

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')
        parser.add_argument('--site', type=int, default=1,
                            help='Django site ID, default: 1')

    def badger(self, attendee, dry_run, site):
        user = attendee.user
        invoice = attendee.new_invoices.first()
        context = Context({
            'invoice_number': invoice.reference_number,
            'name': user.userprofile.display_name(),
            'WAFER_CONFERENCE_DOMAIN': site.domain,
            'WAFER_CONFERENCE_NAME': site.name,
            'DEBCONF_CITY': settings.DEBCONF_CITY,
        })

        txt = Template(TXT).render(context)
        subject = Template(SUBJECT).render(context)
        to = user.email
        if dry_run:
            print('I would badger:', to)
            return
        email_message = EmailMultiAlternatives(subject, txt, to=[to])
        email_message.send()
        invoice.status = 'canceled'
        invoice.save()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')
        site = Site.objects.get(id=1)
        for attendee in Attendee.objects.all():
            if not attendee.user.userprofile.is_registered():
                continue
            if not attendee.new_invoices.exists():
                continue
            if not attendee.billable():
                self.badger(attendee, dry_run, site)
