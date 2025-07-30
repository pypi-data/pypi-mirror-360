import sys

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from wafer.talks.models import Talk


FROM = 'content@debconf.org'

SUBJECT_A = '%(conference)s - talk accepted: %(title)s'
BODY_A = '''\
Dear speaker / BoF organizer,

We are glad to announce that your activity titled
%(title)s
was accepted for presentation at %(conference)s.

We look forward to seeing you in %(city)s.
We will soon start to put the schedule together, so make sure that your arrival
and departure dates are up to date in the system, so we can schedule your
activity on a suitable date.

In case your plans changed and you won't be attending anymore, please let us
know by replying to this email, as soon as possible. Also, please cancel your
conference registration in the conference website.

Our video team has some technical advice for presenters:
https://debconf-video-team.pages.debian.net/docs/advice_for_presenters.html

Best regards,
The %(conference)s Content Team
'''

SUBJECT_R = '%(conference)s - talk not accepted: %(title)s'
BODY_R = '''\
Dear submitter,

Thanks for your interest in %(conference)s.

We are sorry to say that your activity titled
%(title)s
was not accepted for presentation at the %(conference)s main schedule.

Note that %(conference)s will feature ad-hoc sessions where you can still
present your session. Those sessions are not covered by the video team, and so
not streamed or recorded. They are scheduled during the conference, so if you
are interested in presenting, come to %(conference)s, and and look out for an
email announcing the ad-hoc scheduling process.

We look forward to seeing you in %(city)s.

Best regards,
The %(conference)s Content Team
'''

TEMPLATES = {
    'A': {'subject': SUBJECT_A, 'body': BODY_A},
    'R': {'subject': SUBJECT_R, 'body': BODY_R},
}


OPTION_TO_STATUS = {
    'accepted': 'A',
    'not_accepted': 'R',
    'under_consideration': 'U',
    'provisionally_accepted': 'P',
}


class Command(BaseCommand):
    help = "Notify speakers about their talks."

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something'),

        parser.add_argument('--accepted', action='store_true',
                            help='Notify accepted talks'),

        parser.add_argument('--not-accepted', action='store_true',
                            help='Notify rejected talks'),

        parser.add_argument('--provisionally-accepted', action='store_true',
                            help='Notify provisionally accepted talks'),

        parser.add_argument('--under-consideration', action='store_true',
                            help='Notify talks under consideration'),

        parser.add_argument('--subject', type=str, metavar='SUBJECT',
                            help='String to use as subject template for the emails'),

        parser.add_argument('--body', type=open, metavar='BODY',
                            help='File with template for the email body'),

        parser.add_argument('--bcc', type=str, nargs='+',
                            metavar='ADDR',
                            help='Add each ADDR to Bcc:'),

    def badger(self, talk, dry_run, subject_template, body_template, bcc):
        status = talk.get_status_display().lower().replace(' ', '_')
        kv, _ = talk.kv.get_or_create(
            group=self.content_group,
            key='notified_speaker_' + status,
            defaults={'value': None},
        )

        if kv.value:
            return

        to = [user.email for user in talk.authors.all()]

        subst = {
            'title': talk.title,
            'conference': settings.DEBCONF_NAME,
            'city': settings.DEBCONF_CITY,
        }

        subject = subject_template % subst
        body = body_template % subst

        if dry_run:
            print('I would badger speakers of: %s [status=%s]' % (talk.title,
                                                                  talk.status))
            return
        else:
            print('Badgering speakers of: %s' % talk.title)
        email_message = EmailMultiAlternatives(
            subject, body, from_email=FROM, to=to, bcc=bcc)
        email_message.send()

        kv.value = True
        kv.save()

    def handle(self, *args, **options):
        dry_run = not options['yes']
        self.content_group = Group.objects.get_by_natural_key('Talk Mentors')

        if dry_run:
            print('Not actually doing anything without --yes')

        status = None
        for key, value in OPTION_TO_STATUS.items():
            if options[key]:
                if status:
                    print('E: multiple talk statuses informed. Choose only one.')
                    sys.exit(1)
                status = value

        if not status:
            print("E: no talks selected; use --accepted, --not-accepted, etc")
            sys.exit(1)

        if status not in TEMPLATES:
            if not options['subject'] or not options['body']:
                print('E: no built-in template for status "%s"; please provide one explicitly with --subject and --body' % status)
                print('I: example subject template: %s' % TEMPLATES['A']['subject'])
                print('I: example body template:')
                print('----------------8<----------------8<----------------8<-----------------')
                print(TEMPLATES['A']['body'])
                print('----------------8<----------------8<----------------8<-----------------')
                sys.exit(1)

        if options['subject']:
            subject_template = options['subject']
        else:
            subject_template = TEMPLATES[status]['subject']

        if options['body']:
            body_template = options['body'].read()
        else:
            body_template = TEMPLATES[status]['body']

        bcc = options['bcc']

        for talk in Talk.objects.filter(status=status):
            self.badger(talk, dry_run, subject_template, body_template, bcc)
