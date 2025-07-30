from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.utils.timezone import now

from debconf.tz import aoe_datetime
from register.models import Attendee
from wafer.users.models import UserProfile


SUBJECT = '{{ WAFER_CONFERENCE_NAME }}: Registration Reminder'
TXT = '''Hi {{ name }},

{% if other_users %}You have multiple user-accounts on https://{{ WAFER_CONFERENCE_DOMAIN }} with the same email address.
This email concerns the account with username "{{ username }}".
Your other usernames are:
{% for user in other_users %}- {{ user.username }}: {{ user.status }}
{% endfor %}If you have created multiple accounts by accident, please let us know and we can
delete the extra accounts.

{% endif %}{% if incomplete_registration %}We see that you started a registration on https://{{ WAFER_CONFERENCE_DOMAIN }}
but have not yet completed it.
{% else %}We see that you have created an account on https://{{ WAFER_CONFERENCE_DOMAIN }}
but have not yet actually registered to attend the conference.
{% endif %}
If you intend to attend, please go to:
<https://{{ WAFER_CONFERENCE_DOMAIN }}/register/>
and fill out every page of the form.

Once you are successfully registered, you'll receive a confirmation e-mail, and
see a big green "Registered" label on your profile.

{% if incomplete_registration %}If you no longer plan to attend {{ WAFER_CONFERENCE_NAME }}, go to:
<https://{{ WAFER_CONFERENCE_DOMAIN }}/register/unregister>
and click the "Unregister" button.

{% endif %}{% if before_bursary_deadline %}Bursary applications close on {{ DEBCONF_BURSARY_DEADLINE|date:"SHORT_DATE_FORMAT" }} AoE.
If you are applying for a bursary, you need to complete your registration
before this date.
AoE means Anywhere on Earth: You don't have to think about timezones, just
apply before this date, wherever you are in the world.

We recommend that you register as soon as possible.
{% else %}Unfortunately, bursary applications have already closed.

We recommend that you register as soon as possible, if you're planning to
attend at your own cost.
{% endif %}If you need to amend your registration later, you can.

Hope to see you in {{ DEBCONF_CITY }},

The {{ WAFER_CONFERENCE_NAME }} team
'''


class Command(BaseCommand):
    help = "Badger users who haven't registered for attendance"

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')
        parser.add_argument('--site', type=int, default=1,
                            help='Django site ID, default: 1')

    def badger(self, user, dry_run, site):
        bursary_deadline = settings.DEBCONF_BURSARY_DEADLINE
        before_deadline = aoe_datetime(bursary_deadline) > now()
        try:
            attendee = user.attendee
            incomplete_registration = True
        except Attendee.DoesNotExist:
            incomplete_registration = False

        other_users = []
        for other_user in get_user_model().objects.filter(
                email=user.email).exclude(username=user.username):
            if not other_user.is_active:
                other_status = 'Un-verified'
            elif other_user.userprofile.is_registered():
                other_status = 'Registered'
            else:
                try:
                    other_user.attendee
                    other_status = 'Incomplete Registration'
                except Attendee.DoesNotExist:
                    other_status = 'Not Registered'
            other_users.append({
                'username': other_user.username,
                'status': other_status,
            })

        context = Context({
            'name': user.userprofile.display_name(),
            'username': user.username,
            'other_users': other_users,
            'before_bursary_deadline': before_deadline,
            'incomplete_registration': incomplete_registration,
            'DEBCONF_BURSARY_DEADLINE': bursary_deadline,
            'DEBCONF_CITY': settings.DEBCONF_CITY,
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
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')
        site = Site.objects.get(id=1)
        for user in UserProfile.objects.all():
            if not user.is_registered():
                self.badger(user.user, dry_run, site)
