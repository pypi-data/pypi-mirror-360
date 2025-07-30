# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from invoices.models import Invoice
from invoices.stripe_payments import PaymentIntent, build_metadata


class Command(BaseCommand):
    help = 'Update the breakdown metedata on invoices, in Stripe'

    def update_invoice(self, invoice):
        PaymentIntent.modify(invoice.transaction_id,
                             metadata=build_metadata(invoice))

    def handle(self, *args, **options):
        for invoice in Invoice.objects.filter(transaction_id__startswith='pi_'):
            self.update_invoice(invoice)
