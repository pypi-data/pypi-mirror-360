from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.template import Context, Template

from bursary.models import Bursary


SUBJECT = '{{ WAFER_CONFERENCE_NAME }}: Registration Automatically Cancelled'
TXT = '''Dear {{ name }},

We're sorry that we were unable to grant you travel assistance for
{{ WAFER_CONFERENCE_NAME }}.

When you applied for your travel bursary, you informed us that, without the
bursary, you'd be unable to attend the conference. As a result, we have
automatically cancelled your registration.

If you still wish to attend {{ WAFER_CONFERENCE_NAME }}, please go to:
<https://{{ WAFER_CONFERENCE_DOMAIN }}/register/>
and fill out every page of the form.

Thanks for your interest in attending,
The {{ WAFER_CONFERENCE_NAME }} Registration Team
'''


class Command(BaseCommand):
    help = ("Cancel the registration for attendees without travel bursaries "
            "if they listed their level of need as critical")

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')
        parser.add_argument('--site', type=int, default=1,
                            help='Django site ID, default: 1')

    def badger(self, user, dry_run, site):
        context = Context({
            'name': user.userprofile.display_name(),
            'WAFER_CONFERENCE_DOMAIN': site.domain,
            'WAFER_CONFERENCE_NAME': site.name,
        })

        txt = Template(TXT).render(context)
        subject = Template(SUBJECT).render(context)
        to = user.email
        if dry_run:
            print('I would badger:', user.username)
            return
        if user.attendee.billable() and user.attendee.paid():
            print(f"Refusing to cancel {user.username}. "
                  "They have paid an invoice.")
            return
        email_message = EmailMultiAlternatives(subject, txt, to=[to])
        email_message.send()

        user.attendee.delete()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')
        site = Site.objects.get(id=1)
        for bursary in Bursary.objects.filter(
                request_travel=True,
                need='unable',
                travel_status__in=('expired', 'denied', 'canceled')):
            user = bursary.user
            if user.userprofile.is_registered():
                self.badger(user, dry_run, site)
