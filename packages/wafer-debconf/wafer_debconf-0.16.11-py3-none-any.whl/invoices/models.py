from django.conf import settings
from django.core.signing import Signer
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('new', 'Invoiced'),
        ('pending', 'Payment pending'),
        ('paid', 'Payment received'),
        ('canceled', 'Invoice canceled'),
        ('disputed', 'Payment disputed'),
        ('refunded', 'Payment refunded'),
    )

    reference_number = models.CharField(max_length=128, unique=True,
                                        null=False, blank=False)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES,
                              default='new')
    date = models.DateField()

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='invoices',
                                  on_delete=models.PROTECT)
    invoiced_entity = models.CharField(max_length=128, blank=True)
    billing_address = models.TextField()
    compound = models.BooleanField(default=False)

    transaction_id = models.CharField(max_length=128, null=False, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    signer = Signer(sep=':', salt='invoices.Invoice')

    @property
    def total(self):
        return sum(line.total for line in self.lines.all())

    @property
    def total_local(self):
        return round(self.total * settings.DEBCONF_LOCAL_CURRENCY_RATE, 2)

    def text_details(self):
        header = ('Reference', 'Description', 'Qty', 'Unit', 'Total')
        footer = ('', '', '', 'Total', str(self.total))
        lines = [
            (line.reference, line.description, line.quantity, line.unit_price,
             line.total)
            for line in self.lines.all()
        ]
        all_lines = (
            [
                header,
                ('', '', '', '', ''),
            ]
            + lines
            + [
                ('', '', '', '-------', '-------'),
                footer,
            ]
        )

        col_width = [max(len(str(x)) for x in col) for col in zip(*all_lines)]
        formats = ['{:{}}'] * 3 + ['{:>{}}'] * 2
        return "\n".join(
            ("| " + " | ".join(formats[i].format(x, col_width[i])
                               for i, x in enumerate(line)) + " |")
            for line in all_lines
        )

    def save(self, *args, **kwargs):
        # generate reference number on save
        if not self.reference_number:
            year = str(self.date.year)
            last_invoice = Invoice.objects.filter(
                reference_number__startswith=year
            ).order_by('-reference_number').first()

            if last_invoice:
                year, seqnum = last_invoice.reference_number.split('-')
                seqnum = int(seqnum, 10) + 1
            else:
                seqnum = 1

            self.reference_number = '%s-%05d' % (year, seqnum)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'invoices:display',
            kwargs={'reference_number': self.reference_number})

    def get_signed_url(self):
        signed_reference = self.signer.sign(self.reference_number)
        return reverse(
            'invoices:display',
            kwargs={'reference_number': signed_reference})

    def get_payment_intent(self):
        # FIXME: Replace with better column
        from invoices.stripe_payments import payment_intent
        return payment_intent(self)

    def income_breakdown(self):
        summary = {}
        for line in self.lines.all():
            if line.reference.startswith('INV#'):
                # There are two types of existing invoices:
                # Combined invoices have a positive sign
                # Previous payments have a negative sign
                sign = 1 if line.total >= 0 else -1
                ref = line.reference.split('#', 1)[1]
                try:
                    sub_invoice = Invoice.objects.get(reference_number=ref)
                except Invoice.DoesNotExist:
                    continue
                for category, value in sub_invoice.income_breakdown().items():
                    summary[category] = summary.get(category, 0) + value * sign
            else:
                category = line.breakdown_category
                if category == 'refund':  # We use stripe's total for refunds
                    continue
                summary[category] = summary.get(category, 0) + line.total
        return summary


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='lines',
                                on_delete=models.CASCADE)
    line_order = models.IntegerField()
    reference = models.CharField(max_length=32)
    description = models.CharField(max_length=1024)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    @property
    def total(self):
        return self.unit_price * self.quantity

    class Meta:
        unique_together = ('invoice', 'line_order')
        ordering = ('invoice', 'line_order')

    def __str__(self):
        return 'InvoiceLine(%s [%s] %d @ %.02f = %.02f)' % (
            self.reference,
            self.description,
            self.quantity,
            self.unit_price,
            self.total,
        )

    @property
    def breakdown_category(self):
        ref = self.reference
        if ref.startswith(settings.INVOICE_PREFIX):
            ref = ref[len(settings.INVOICE_PREFIX):].split('-')[0]
        return {
            'REG': 'registration',
            'ACCOMM': 'accommodation',
            'BREAKFAST': 'meals',
            'BRUNCH': 'meals',
            'LUNCH': 'meals',
            'DINNER': 'meals',
            'CONFDINNER': 'meals',
            'CONTRIB': 'contrib',
            'SPONSOR': 'sponsorship',
            'DAYTRIP': 'daytrip',
            'REFUND': 'refund',
        }.get(ref, 'registration')
