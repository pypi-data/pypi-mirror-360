from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from wafer.talks.models import Talk


FROM = 'content@debconf.org'
SUBJECT = '%(conference)s - talk scheduled: %(title)s'
BODY = '''\
Dear speaker / BoF convenor,

We are glad to announce that we have just published the %(conference)s schedule:

https://%(site)s/schedule/

Your Talk/BoF titled %(title)s
has been scheduled at %(time)s in %(venue)s.

We kindly request that you check whether you are able to be there at the day
and time we have allocated to your session. If not, please let us know, by
replying to this email, as soon as possible. We can either reschedule you in a
more convenient time, or if you cannot join us, we will be able to mark the
slot as available for other activities.

Best regards,
The DebConf Content Team
'''


class Command(BaseCommand):
    help = "Notify speakers that their talks have been scheduled"

    def add_arguments(self, parser):
        parser.add_argument('--subject', type=str, metavar='SUBJECT',
                            help='String to use as subject template for the emails'),
        parser.add_argument('--body', type=open, metavar='BODY',
                            help='File with template for the email body'),
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),
        parser.add_argument('--again', action='store_true',
                            help='Mail all speakers, even those who were already contacted'),

    def badger(self, talk, dry_run, again, subject_template, body_template):
        try:
            scheduleitem = talk.scheduleitem_set.get()
        except ObjectDoesNotExist:
            return

        kv, created = talk.kv.get_or_create(
            group=self.content_group,
            key='notified_speaker',
            defaults={'value': None},
        )

        rebadger_key = [scheduleitem.venue.id, scheduleitem.slots.first().id]
        if kv.value == rebadger_key and not again:
            return

        to = [user.email for user in talk.authors.all()]

        site = Site.objects.first().domain
        subst = {
            'title': talk.title,
            'time': scheduleitem.get_start_time(),
            'venue': scheduleitem.venue.name,
            'conference': settings.DEBCONF_NAME,
            'site': site,
        }

        subject = subject_template % subst
        body = body_template % subst

        if dry_run:
            print('I would badger speakers of: %s'
                  % talk.title)
            return
        email_message = EmailMultiAlternatives(
            subject, body, from_email=FROM, to=to)
        email_message.send()

        kv.value = rebadger_key
        kv.save()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        again = options['again']
        self.content_group = Group.objects.get_by_natural_key('Talk Mentors')

        if dry_run:
            print('Not actually doing anything without --yes')

        subject = options.get("subject") or SUBJECT
        body = options["body"] and options["body"].read() or BODY
        for talk in Talk.objects.all():
            self.badger(talk, dry_run, again, subject, body)
