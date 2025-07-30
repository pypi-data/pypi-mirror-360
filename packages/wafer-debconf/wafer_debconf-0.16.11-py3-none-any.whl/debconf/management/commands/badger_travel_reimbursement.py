# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from django.template import Context, Template

from django.contrib.sites.models import Site

from bursary.models import Bursary

SUBJECT_TEMPLATE = Template(
    '[Action needed] Reimbursement process for {{ WAFER_CONFERENCE_NAME }} '
    'travel bursary recipients')

BODY_TEMPLATE = Template("""\
{% autoescape off %}
Dear {{ object.user.get_full_name }},

You have been granted a travel bursary for DebConf, and now is the time to
submit documentation for reimbursement. TL;DR: yes, this email is very long,
but it is all important, you need to read it in full to get travel money back!

Reimbursement for DebConf-related expenses will be processed by  Debian France
for reimbursements in EUR (typically Pan-European travelers) and Software in
the Public Interest (SPI) for US and other non-EUR reimbursment requests.

The amount you requested is {{ object.travel_bursary }} {{ DEBCONF_BURSARY_CURRENCY }}, and this is therefore the maximum you'll
be able to request for reimbursement.
This does not have to be requested *in* {{ DEBCONF_BURSARY_CURRENCY }}, you can request an equivalent
amount in your home currency (via SPI).

To process the hundreds of reimbursement requests efficiently and
expeditiously, our supporting organizations require complete, readable and
quality controlled submissions, so please take a moment extra to double check
you have everything in order before sending off that final email.

For ̲D̲e̲b̲i̲a̲n̲ ̲F̲r̲a̲n̲c̲e (EUR reimbursements, typically flights, trains and ferries):

Please scan your receipts and attach them to an email to
treasurer-debianfr@rt.debian.org.
You ̲m̲u̲s̲t include "Debian RT - {{ WAFER_CONFERENCE_NAME }} reimbursement for your full name"
in the subject line.
Put tresorier@france.debian.net in CC.

Put the following information into your email:

1. Your full legal name
2. Your bank account details (account owner, IBAN and BIC, ...)
3. Digital copies of your receipts
4. The following text:

--- BEGIN TICKET TEXT ---
By submitting this reimbursement request, I declare:
 • that I have attached sufficient documentation substantiating my request,
 • that I seek reimbursement of expenses that are compliant to DebConf policies, and
 • that I have not sought nor will seek reimbursement of these expenses from any other source.

The amount I am claiming for reimbursement is XXX.XX EUR (out of {{ object.travel_bursary }} {{ DEBCONF_BURSARY_CURRENCY }} allocated).
---- END TICKET TEXT ----

(adjust the reimbursement total so it matches the total of your receipts)

For ̲S̲P̲I (non-EUR reimbursements, typically cross-continental travel):

All requests must include:

 1. an SPI Reimbursement Request Form [1] with accurate banking information as
    SPI uses TransferWise [2]
 2. an Expense Report generated using XE's Travel Expenses Calculator [3]
 3. sufficient documentation substantiating the expense report
 4. a declaration of compliance

And must be submitted to the debconf-reimbursements RT queue (instead of the
normal SPI reimbursement RT queue, listed on [1]).

[1]: https://spi-inc.org/treasurer/reimbursement-form/
[2]: https://transferwise.com
[3]: https://www.xe.com/travel-expenses-calculator/

Requesters must follow these steps:

Step 1: Prepare an Expense Report.
 • use https://www.xe.com/travel-expenses-calculator/ to prepare an expense
   report
 • enter Your Name
 • set Your Home Currency to the currency of your bank account.
 • leave/set Credit Card @ 3%, Debit Card @ 5%, Foreign Cash @ 5%, Traveler's
   Cheque @ 2%
 • enter Receipt Details, one row per receipt
   • specify the correct date of the transactions
   • set the currency per transaction to the currency you paid in
 • save as PDF

Step 2: Prepare an SPI Reimbursement Request Form
 • visit https://spi-inc.org/treasurer/reimbursement-form/
 • fill out the form and download the completed PDF
 • ensure your name exactly matches the Expense Report from Step 1
 • ̲e̲n̲s̲u̲r̲e̲ ̲t̲h̲a̲t̲ ̲t̲h̲e̲ ̲b̲a̲n̲k̲i̲n̲g̲ ̲i̲n̲f̲o̲r̲m̲a̲t̲i̲o̲n̲ ̲i̲s̲ ̲a̲c̲c̲u̲r̲a̲t̲e̲ ̲a̲s̲ ̲i̲n̲c̲o̲r̲r̲e̲c̲t̲ ̲d̲e̲t̲a̲i̲l̲s̲ ̲a̲r̲e̲ ̲a
   ̲m̲a̲j̲o̲r̲ ̲s̲o̲u̲r̲c̲e̲ ̲o̲f̲ ̲d̲e̲l̲a̲y̲s
 • the currency field is the currency of your bank account. Only say {{ DEBCONF_BURSARY_CURRENCY }}
   here if you have a {{ DEBCONF_BURSARY_CURRENCY }} bank account (e.g. because you live there)
 • save as PDF

Step 3: Collect and order your Receipts.
 • collect your receipts in the SAME ORDER as the rows in the Expense Report
 • if paper receipts, scan them with a multi-function device, converting to PDF
 • save as PDF

Step 4: Prepare the Submission Package.
 • collect into a single PDF, the following:
   • from step 2, the SPI Reimbursement Request From
   • from step 1, the Expense Report
   • from step 3, the Ordered Receipts
 • the poppler-utils package includes the pdfunite utility
   • usage: `pdfunite step2.pdf step1.pdf step3a.pdf step3b.pdf ... step3n.pdf {{ WAFER_CONFERENCE_NAME }}ReimbursementRequest-{{ short_full_name }}.pdf`
   • warning: ensure that you explicitly mention the destination filename
     ({{ WAFER_CONFERENCE_NAME }}ReimbursementRequest-{{ short_full_name }}.pdf)
     otherwise step3n.pdf is overwritten
   • notice: please name the file exactly as shown, substituting your name as
     entered in the SPI Reimbursement Request Form, for example,
     {{ WAFER_CONFERENCE_NAME }}ReimbursementRequest-{{ short_full_name }}.pdf
 • ̲e̲n̲s̲u̲r̲e̲ ̲t̲h̲a̲t̲ ̲t̲h̲e̲ ̲e̲n̲t̲i̲r̲e̲ ̲S̲u̲b̲m̲i̲s̲s̲i̲o̲n̲ ̲P̲a̲c̲k̲a̲g̲e̲ ̲c̲a̲n̲ ̲b̲e̲ ̲e̲a̲s̲i̲l̲y̲ ̲u̲n̲d̲e̲r̲s̲t̲o̲o̲d̲ ̲a̲s̲ ̲p̲o̲o̲r
   ̲q̲u̲a̲l̲i̲t̲y̲ ̲s̲u̲b̲m̲i̲s̲s̲i̲o̲n̲s̲ ̲a̲r̲e̲ ̲a̲ ̲m̲a̲j̲o̲r̲ ̲s̲o̲u̲r̲c̲e̲ ̲o̲f̲ ̲d̲e̲l̲a̲y̲s

Step 5: Email the Submission Package.
 • prepare an email having these attributes
   • from: you
   • To: debconf-reimbursements@rt.spi-inc.org
   • subject: {{ WAFER_CONFERENCE_NAME }} Reimbursement Request for {{ object.user.get_full_name }}
   • attachment: the Submission Package ({{ WAFER_CONFERENCE_NAME }}ReimbursementRequest-{{ short_full_name }}.pdf) prepared in step 4
   • body: (the text below, please fix the claimed amount in the last line to
            match your actual request, in your local currency)
--- BEGIN TICKET TEXT ---
By submitting this reimbursement request, I declare:
 • that I have accurately prepared an SPI Reimbursement Request Form,
 • that I have prepared an Expense Report using XE's Travel Expense Calculator,
 • that I have attached sufficient documentation substantiating my request,
 • that I seek reimbursement of expenses that are compliant to DebConf policies, and
 • that I have not sought nor will seek reimbursement of these expenses from any other source.

The amount I am claiming for reimbursement is XXXX.XX your local currency or USD (out of {{ object.travel_bursary }} {{ DEBCONF_BURSARY_CURRENCY }} allocated).
---- END TICKET TEXT ----

If you have any question, please be sure to contact us at bursaries@debconf.org
and we'll work your issues out.

Thanks for your cooperation!
--\u0020
The DebConf Bursaries team
{% endautoescape %}
""")


class Command(BaseCommand):
    help = 'Send an email to people whose bursary grant expires soon'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually send emails')

    def badger(self, bursary, conference_name, dry_run):
        context = {
            'object': bursary,
            'user': bursary.user.username,
            'to': '%s <%s>' % (bursary.user.get_full_name(),
                               bursary.user.email),
            'short_full_name': bursary.user.get_full_name().replace(' ', '')
                                                           .replace('-', '')
                                                           .replace("'", '')
                                                           .replace('.', ''),
            'DEBCONF_BURSARY_CURRENCY': settings.DEBCONF_BURSARY_CURRENCY,
            'WAFER_CONFERENCE_NAME': conference_name,
        }

        if dry_run:
            print('I would badger {to} (max = {object.travel_bursary})'
                  .format(**context))
            return

        from_email = 'bursaries@debconf.org'
        ctx = Context(context)
        subject = SUBJECT_TEMPLATE.render(ctx)
        body = BODY_TEMPLATE.render(ctx)

        msg = EmailMultiAlternatives(subject, body, to=[context['to']],
                                     from_email=from_email)

        msg.send()

    def handle(self, *args, **options):
        site = Site.objects.get()
        conference_name = site.name.replace(' ', '')
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        to_badger = Bursary.objects.filter(
            request_travel=True,
            travel_status='accepted',
            user__attendee__check_in__pk__isnull=False,
            reimbursed_amount=0,
        ).order_by('user__username')

        for bursary in to_badger:
            self.badger(bursary, conference_name, dry_run)
