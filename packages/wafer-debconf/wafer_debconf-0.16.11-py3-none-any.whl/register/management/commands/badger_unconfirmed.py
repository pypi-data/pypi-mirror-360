from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.utils.timezone import now

from debconf.tz import aoe_datetime
from register.models import Attendee


SUBJECT = '''Please confirm your {{ WAFER_CONFERENCE_NAME }} attendance'''

TXT = '''Hi {{ name }},

{{ WAFER_CONFERENCE_NAME }} is coming up soon. Please confirm your attendance
so that we can get accurate attendee numbers.

We have you registered as:
Arriving on {{ arrival }}
Departing on {{ departure }}

To confirm your attendance, please go through the registration form once again.
You need to set final arrival and departure dates, select the "My dates are
final" entry and tick the "I confirm my attendance" box.
You need to go through the wizard *until the end* for your confirmation to
be valid! This makes it a perfect time to review your full registration data.

<https://{{ WAFER_CONFERENCE_DOMAIN }}/register/>

{% if before_deadline %}The deadline for confirmation is {{ DEBCONF_CONFIRMATION_DEADLINE|date:"SHORT_DATE_FORMAT" }} AoE
(AoE = Anywhere on Earth: Forget about timezones, just do it by this date)

{% endif %}{% if invoice %}Our records indicate that you haven't settled your invoice for {{ invoice.total }} {{ DEBCONF_BILLING_CURRENCY }}.

While we do accept cash payment on-site, we would strongly prefer if you
settled the invoice directly online, by going to your profile on the DebConf
website. We will not have credit-card facilities available on-site.

<https://{{ WAFER_CONFERENCE_DOMAIN }}/accounts/profile/>

{% endif %}If you no longer plan to attend {{ WAFER_CONFERENCE_NAME }}, go to:
<https://{{ WAFER_CONFERENCE_DOMAIN }}/register/unregister>
and click the "Unregister" button.

See you soon in {{ DEBCONF_CITY }},

The {{ WAFER_CONFERENCE_NAME }} Registration Team
'''


class Command(BaseCommand):
    help = "Badger users who haven't confirmed registration for attendance"

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')
        parser.add_argument('--site', type=int, default=1,
                            help='Django site ID, default: 1')

    def badger(self, user, dry_run, site):
        attendee = user.attendee
        invoice = attendee.new_invoices.first()
        confirmation_deadline = settings.DEBCONF_CONFIRMATION_DEADLINE
        before_deadline = aoe_datetime(confirmation_deadline) > now()
        context = Context({
            'name': user.userprofile.display_name(),
            'arrival': attendee.arrival,
            'before_deadline': before_deadline,
            'departure': attendee.departure,
            'invoice': invoice,
            'DEBCONF_BILLING_CURRENCY': settings.DEBCONF_BILLING_CURRENCY,
            'DEBCONF_CITY': settings.DEBCONF_CITY,
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
