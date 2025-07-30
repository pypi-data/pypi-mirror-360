from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.template import Context, Template

from register.models import Attendee


SUBJECT = ('[ACTION REQUIRED]: Are you coming to {{ WAFER_CONFERENCE_NAME }}? '
           'Confirm your attendance *now*!')

TXT = """\
Dear {{ name }},

Our records indicate that you haven't confirmed your attendance at {{ WAFER_CONFERENCE_NAME }}.

The deadline for confirmation is {{ DEBCONF_CONFIRMATION_DEADLINE|date:"SHORT_DATE_FORMAT" }} AoE.
(AoE = Anywhere on Earth: Forget about timezones, just do it by this date)
After this date, we cannot guarantee any accommodation or food that you may
have requested. Your badge may not be printed and we probably won't have a
t-shirt or swag to offer you, either.

To confirm your attendance, go through the registration form once again.
You need to set final arrival and departure dates, select the "My dates are
final" entry and tick the "I confirm my attendance" box. Then go through the
rest of the form verifying your data and Save.

<https://{{ WAFER_CONFERENCE_DOMAIN }}/register/>

If you no longer plan to attend {{ WAFER_CONFERENCE_NAME }}, go to:
<https://{{ WAFER_CONFERENCE_DOMAIN }}/register/unregister>
and click the "Unregister" button.

Thank you,

The {{ WAFER_CONFERENCE_NAME }} Registration Team
"""


class Command(BaseCommand):
    help = "Final badger for users who haven't confirmed registration for attendance"

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')
        parser.add_argument('--site', type=int, default=1,
                            help='Django site ID, default: 1')

    def badger(self, user, dry_run, site):
        confirmation_deadline = settings.DEBCONF_CONFIRMATION_DEADLINE
        context = Context({
            'name': user.userprofile.display_name(),
            'DEBCONF_CONFIRMATION_DEADLINE': confirmation_deadline,
            'WAFER_CONFERENCE_DOMAIN': site.domain,
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
        if not settings.RECONFIRMATION:
            print('Set RECONFIRMATION=True and try again')
            return

        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')
        site = Site.objects.get(id=1)
        for attendee in Attendee.objects.filter(reconfirm=False):
            user = attendee.user
            if user.userprofile.is_registered():
                self.badger(user, dry_run, site)
