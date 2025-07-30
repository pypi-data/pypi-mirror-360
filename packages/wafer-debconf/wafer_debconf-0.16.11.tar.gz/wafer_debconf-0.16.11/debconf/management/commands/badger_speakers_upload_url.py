import sys
import yaml

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from wafer.talks.models import TalkUrl
from wafer.schedule.models import ScheduleItem


FROM = 'content@debconf.org'

SUBJECT = '%(conference)s - upload URL for %(title)s'
BODY = '''\
Dear speaker,

We strongly recommend that you pre-record your talk
%(title)s

We will stream the talk, then follow it with a live Q&A session via Jitsi,
provided there is time.  Guidelines on how to record your talk can be found at
<https://debconf-video-team.pages.debian.net/docs/advice_for_recording.html>.
If you have any questions, please contact the content team on the
#debconf-content IRC channel on the OFTC network, or by email via
content@debconf.org.

When you are done with your recording, please upload it here:
%(url)s

If your session is not a "talk", but a BoF, or any other type of acvitity that
needs to happen live, just ignore this message.

Best regards,
The %(conference)s Content Team
'''


class Command(BaseCommand):
    help = "Notify speakers about their talks."

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),
        parser.add_argument('urls', type=open, metavar='URLFILE',
                            help='File with urls data (format: yaml dict with guid (from ScheduleItem) as key, url as value)'),

    def notify(self, talk, url, dry_run):
        kv, _ = talk.kv.get_or_create(
            group=self.content_group,
            key='notified_speaker_upload_url',
            defaults={'value': None},
        )

        if kv.value == url:
            return

        to = [user.email for user in talk.authors.all()]

        subst = {
            'title': talk.title,
            'conference': settings.DEBCONF_NAME,
            'url': url,
        }

        subject = SUBJECT % subst
        body = BODY % subst

        if dry_run:
            print('I would badger speakers of: %s' % talk.title)
            return
        else:
            print('Badgering speakers of: %s' % talk.title)
        email_message = EmailMultiAlternatives(
            subject, body, from_email=FROM, to=to)
        email_message.send()

        TalkUrl.objects.create(
            description="upload",
            url=url,
            talk=talk,
            public=False,
        )

        kv.value = url
        kv.save()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')

        self.content_group = Group.objects.get_by_natural_key('Talk Mentors')
        urls = yaml.load(options["urls"])
        for item in ScheduleItem.objects.all():
            if not item.talk:
                continue
            talk = item.talk
            url = urls.get(str(item.guid))
            if url:
                self.notify(talk, url, dry_run)
            else:
                print("W: no URL for \"%s\" found" % (talk.title))
