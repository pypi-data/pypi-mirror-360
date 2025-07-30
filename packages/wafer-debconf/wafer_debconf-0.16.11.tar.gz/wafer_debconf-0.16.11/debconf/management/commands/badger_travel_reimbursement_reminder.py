# -*- coding: utf-8 -*-

from datetime import date, timedelta

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from django.template import Context, Template

from django.contrib.sites.models import Site

from bursary.models import Bursary

SUBJECT_TEMPLATE = Template(
    '[{% if final %}FINAL {% endif %}REMINDER] Reimbursement process for '
    '{{ WAFER_CONFERENCE_NAME }} travel bursary recipients')

BODY_TEMPLATE = Template("""\
{% autoescape off %}
Dear {{ object.user.get_full_name }},

According to our records, you still haven't requested your travel bursary
reimbursement for {{ WAFER_CONFERENCE_NAME }}.

{% if final %}
This is the FINAL REMINDER. You have 3 weeks to claim your reimbursement,
before we close the process. The deadline is {{ final_deadline|date }}.

{% endif %}
If you still plan to collect your reimbursement, please do so ASAP. You can
find the instructions in the previous email on the subject.

If you don't intend to collect it, please reply to this e-mail.

If you're having any trouble with the process, please reply to this email and
let us help you.

Thank you
--\u0020
The DebConf Bursaries team
{% endautoescape %}
""")


class Command(BaseCommand):
    help = "Send an email to people who haven't claimed their travel bursary yet"

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually send emails')
        parser.add_argument('--final', action='store_true',
                            help='Give a 3-week final deadline')

    def badger(self, bursary, conference_name, dry_run, final):
        context = {
            'object': bursary,
            'user': bursary.user.username,
            'to': '%s <%s>' % (bursary.user.get_full_name(),
                               bursary.user.email),
            'final': final,
            'final_deadline': date.today() + timedelta(weeks=3),
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
            self.badger(bursary, conference_name, dry_run, options['final'])
