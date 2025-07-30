# -*- coding: utf-8 -*-

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from django.template import Context, Template

from django.contrib.sites.models import Site

from register.models import Attendee

SUBJECT_TEMPLATE = Template('Feedback for {{ WAFER_CONFERENCE_NAME }}')

BODY_TEMPLATE = Template("""\
{% autoescape off %}
Dear {{ attendee.user.get_full_name }},

We hope you're all adjusting back to your day-to-day post-DebConf lives, and
that your travels back were safe and uneventful.

We'd like to hear your thoughts about this DebConf: was there anything you
particularly liked? Or perhaps something you really think should have been done
differently?

DebConf values your feedback! Please get in touch with us at:
<feedback@debconf.org>

Both suggestions for improvement and positive feedback are very welcome, and
will be anonymised, then passed along to the relevant teams.

Best regards,

The {{ WAFER_CONFERENCE_NAME }} Team
{% endautoescape %}
""")


class Command(BaseCommand):
    help = 'Send a feedback request email to attendees who arrived'

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually send emails')

    def badger(self, attendee, conference_name, dry_run):
        context = {
            'attendee': attendee,
            'to': '%s <%s>' % (attendee.user.get_full_name(),
                               attendee.user.email),
            'WAFER_CONFERENCE_NAME': conference_name,
        }

        if dry_run:
            print('I would badger {to}'.format(**context))
            return

        from_email = 'feedback@debconf.org'
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

        to_badger = Attendee.objects.filter(
            check_in__pk__isnull=False,
        ).order_by('user__username')

        for attendee in to_badger:
            self.badger(attendee, conference_name, dry_run)
