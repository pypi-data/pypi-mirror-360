# -*- coding: utf-8 -*-
import datetime

from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template import Context, Template

from bursary.models import Bursary

SUBJECT_TEMPLATE = Template(
    "[Action needed] Your {{WAFER_CONFERENCE_NAME}} travel bursary grant "
    "expires in {{days}} day{{days|pluralize}}!")

BODY_TEMPLATE = Template("""\
Dear {{object.user.get_full_name}},

Your travel bursary request has been granted by the bursaries team, and you
have not confirmed it yet.

You need to do so before {{ object.travel_accept_before|date }} at 23:59 UTC,
or you will no longer be eligible for this bursary. The budget we have
allocated for you will be redistributed to other applicants.

Please log into the website at https://{{ domain }}/bursary/ to update
your status.

If you're unable to do so before the deadline, let us know by replying to this
message and we'll work something out.

Thanks!
--\u0020
The DebConf Bursaries team
""")


class Command(BaseCommand):
    help = 'Send an email to people whose bursary grant expires soon'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually send emails')
        parser.add_argument('--days-before', '-d', metavar='X,Y',
                            default='6,3,1',
                            help='Send reminders for bursaries expiring X and '
                                 'Y days in the future (comma-separated list, '
                                 'defaults to 6,3,1)')


    def badger(self, bursary, dry_run):
        site = Site.objects.get()
        conference_name = site.name.replace(' ', '')

        context = {
            'WAFER_CONFERENCE_NAME': conference_name,
            'domain': site.domain,
            'object': bursary,
            'user': bursary.user.username,
        }

        delta = bursary.travel_accept_before - datetime.datetime.today().date()
        context['days'] = delta.days

        if dry_run:
            print('I would badger {user} (expiry in {days} days)'
                  .format(**context))
            return

        from_email = 'bursaries@debconf.org'
        to = bursary.user.email
        subject = SUBJECT_TEMPLATE.render(Context(context))
        body = BODY_TEMPLATE.render(Context(context))

        msg = EmailMultiAlternatives(subject, body, to=[to],
                                     from_email=from_email)

        msg.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')
        days_before = [int(x) for x in options['days_before'].split(',')]

        dates = [
            (datetime.datetime.today().date()
             + datetime.timedelta(days=days))
            for days in days_before
        ]

        if dry_run:
            for date in dates:
                print('Will badger for expiry on %s' % date)

        to_badger = Bursary.objects.filter(
            request_travel=True,
            travel_status='pending',
            travel_accept_before__in=dates,
        )

        for bursary in to_badger:
            self.badger(bursary, dry_run)
