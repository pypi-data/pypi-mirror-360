from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.template import Context, Template

from register.models import Attendee
from register.views import STEPS


SUBJECT = '{{ WAFER_CONFERENCE_NAME }}: Incomplete Registration'
TXT = '''Hi {{ name }},

We see you started a registration for {{ WAFER_CONFERENCE_NAME }}, but never
completed it.  This means you are not currently registered to attend.
Registration is only complete once you have gone through all the steps and
received a confirmation mail.  If you still plan to attend DebConf, please go
visit the registration page and complete all the steps.

{% if billable %}This will generate an invoice.{% endif %}

Best regards,

The {{ WAFER_CONFERENCE_NAME }} team
'''


class Command(BaseCommand):
    help = "Badger users who started but didn't finish registration"

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')
        parser.add_argument('--site', type=int, default=1,
                            help='Django site ID, default: 1')

    def badger(self, user, dry_run, site):
        context = Context({
            'name': user.userprofile.display_name(),
            'billable': user.attendee.billable(),
            'WAFER_CONFERENCE_NAME': site.name,
        })

        txt = Template(TXT).render(context)
        subject = Template(SUBJECT).render(context)
        to = user.email
        if dry_run:
            print('I would badger:', to)
            return
        email_message = EmailMultiAlternatives(subject, txt, to=[to])
        email_message.send()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')
        site = Site.objects.get(id=1)
        for attendee in Attendee.objects.filter(completed_register_steps__lt=len(STEPS) - 1):
            self.badger(attendee.user, dry_run, site)
