from datetime import datetime
import logging

from django.conf import settings

import stripe
from stripe import PaymentIntent

from invoices.models import Invoice, InvoiceLine

stripe.api_key = settings.STRIPE_SECRET_KEY
log = logging.getLogger(__name__)


def build_metadata(invoice):
    """Generate metadata that we can use in our books"""
    metadata = {
        'reference_number': invoice.reference_number,
    }
    for category, value in invoice.income_breakdown().items():
        if value:  # Follow-up invoices are likely to contain 0 values, strip
            metadata[f'breakdown_{category}'] = float(value)
    return metadata


def payment_intent(invoice):
    ref = invoice.reference_number
    total_cents = int(invoice.total * 100)
    intent = None
    if invoice.transaction_id:
        intent = PaymentIntent.retrieve(invoice.transaction_id)
    if intent and intent.status == 'canceled':
        log.warn('Stripe PaymentIntent unexpectedly canceled for %s', ref)
        intent = None
    if intent is None:
        log.info('Creating Stripe PaymentIntent for %s', ref)
        intent = PaymentIntent.create(
            amount=total_cents,
            currency=settings.DEBCONF_BILLING_CURRENCY,
            description='DebConf Invoice {}'.format(ref),
            metadata=build_metadata(invoice),
        )
        invoice.transaction_id = intent.id
        invoice.save()
    if intent.status == 'succeeded':
        log.warn('Stripe PaymentIntent unexpectedly succeeded for %s', ref)
        payment_received(invoice, intent)
        return intent
    if intent.amount != total_cents:
        log.info('Updating PaymentIntent amount for %s', ref)
        intent = PaymentIntent.modify(intent.id, amount=total_cents)
    return intent


def payment_intent_succeeded(intent, ignore_unrelated=False):
    """A payment_intent has succeeded"""
    reference_number = intent.metadata.get('reference_number')
    try:
        invoice = Invoice.objects.get(reference_number=reference_number,
                                      transaction_id=intent.id)
    except Invoice.DoesNotExist:
        if not ignore_unrelated:
            raise
        log.info('Ignoring payment_intent.created for unrelated intent %s',
                 intent.id)
        return
    payment_received(invoice, intent)


def payment_received(invoice, intent):
    total_cents = int(invoice.total * 100)
    if intent.amount != total_cents:
        log.error('Received amount $%s (%s) does not match invoice $%s (%s)',
                  intent.amount / 100.0, intent.id, invoice.total, invoice.id)
        return

    if invoice.status == 'paid':
        # We expect to race between re-rendering the invoice and receiving a
        # webhook.
        return
    if invoice.status not in ('new', 'pending'):
        log.error('Refusing to mark invoice %s as paid (%s) when status is %s',
                  invoice.id, intent.id, invoice.status)
        return

    invoice.status = 'paid'
    invoice.transaction_id = intent.id
    invoice.save()

    if invoice.compound:
        for line in invoice.lines.all():
            reference = line.reference.split('#', 1)[1]
            child_invoice = Invoice.objects.get(reference_number=reference)
            child_invoice.status = 'paid'
            child_invoice.transaction_id = intent.id
            child_invoice.save()


def charge_refunded(charge, ignore_unrelated=False):
    """A payment has been refunded"""
    if not charge.payment_intent:
        log.error('charge.refunded (%s) for charge without intent', charge.id)
        return
    intent = PaymentIntent.retrieve(charge.payment_intent)
    reference_number = intent.metadata.get('reference_number')
    try:
        invoice = Invoice.objects.get(reference_number=reference_number,
                                      transaction_id=intent.id,
                                      status__in=('paid', 'pending'))
    except Invoice.DoesNotExist:
        if not ignore_unrelated:
            raise
        log.info('Ignoring charge.refunded for unrelated intent %s',
                 intent.id)
        return
    if charge.amount_captured == charge.amount_refunded:
        # Full Refund
        invoice.status = 'refunded'
        invoice.save()
    else:
        # Partial Refund
        refund = charge.refunds["data"][0]
        if refund["status"] != "succeeded":
            log.info("Refund isn't complete. Ignoring: %r", refund)
            return
        amount = refund["amount"]
        created = datetime.fromtimestamp(refund["created"])
        line_order = invoice.lines.last().line_order + 1
        line = InvoiceLine(
            invoice=invoice,
            reference='REFUND',
            line_order=line_order,
            description='Partial Refund Issued on: {}'.format(created.isoformat()),
            unit_price=-amount / 100,
            quantity=1,
        )
        line.save()


def dispute_filed(dispute, ignore_unrelated=False):
    """A charge has been disputed"""
    if not dispute.payment_intent:
        log.error('charge.dispute.created (%s) for charge without intent',
                  dispute.id)
        return
    intent = PaymentIntent.retrieve(dispute.payment_intent)
    reference_number = intent.metadata.get('reference_number')
    try:
        invoice = Invoice.objects.get(reference_number=reference_number,
                                      transaction_id=intent.id,
                                      status__in=('paid', 'pending'))
    except Invoice.DoesNotExist:
        if not ignore_unrelated:
            raise
        log.info('Ignoring charge.dispute.created for unrelated intent %s',
                 intent.id)
        return
    invoice.status = 'disputed'
    invoice.save()
