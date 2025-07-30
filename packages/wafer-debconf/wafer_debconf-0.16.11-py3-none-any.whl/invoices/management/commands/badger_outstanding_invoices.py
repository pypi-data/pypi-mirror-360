# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import get_template

from django.contrib.sites.models import Site

from invoices.models import Invoice


class Command(BaseCommand):
    help = 'Badger outstanding invoices'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),
        parser.add_argument('--confirmed', action='store_true',
                            help='Only consider attendees who confirmed')
        parser.add_argument('--arrived', action='store_true',
                            help='Only consider attendees who arrived')

    def badger(self, invoice, dry_run):
        to = invoice.recipient.email
        name = invoice.recipient.get_full_name()
        invoice_number = invoice.reference_number
        total = invoice.total
        currency = settings.DEBCONF_BILLING_CURRENCY
        site = Site.objects.first()

        if not total:
            return

        if dry_run:
            print(f'I would badger {name} <{to}> '
                  f'({invoice_number}: {total} {currency})')
            return

        ctx = {
            'name': name,
            'total': total,
            'currency': currency,
            'invoice_number': invoice_number,
            'invoice_details': invoice.text_details(),
            'WAFER_CONFERENCE_NAME': site.name,
            'WAFER_CONFERENCE_DOMAIN': site.domain,
        }

        template = get_template('invoices/outstanding_invoices-subject.txt')
        subject = template.render(ctx).strip()

        template = get_template('invoices/outstanding_invoices-body.txt')
        body = template.render(ctx)

        email_message = EmailMultiAlternatives(subject, body,
                                               to=["%s <%s>" % (name, to)])
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        for invoice in Invoice.objects.filter(status='new'):
            if invoice.recipient.userprofile.is_registered():
                attendee = invoice.recipient.attendee
                if options['confirmed'] and not attendee.confirmed():
                    continue
                if options['arrived'] and not attendee.arrived:
                    continue
                self.badger(invoice, dry_run)
