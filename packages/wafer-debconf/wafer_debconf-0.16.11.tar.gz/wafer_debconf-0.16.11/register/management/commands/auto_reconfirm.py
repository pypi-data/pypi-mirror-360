from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from register.models import Attendee


class Command(BaseCommand):
    help = ("Automatically reconfirm attendees who have accepted a bursary or "
            "paid an invoice (and have final dates)")

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')

    def check_reconfirm(self, attendee, dry_run):
        if attendee.billable() and attendee.paid():
            return self.reconfirm(attendee, dry_run)
        try:
            bursary = attendee.user.bursary
        except ObjectDoesNotExist:
            pass
        else:
            if bursary.status_in(None, ['accepted']):
                return self.reconfirm(attendee, dry_run)

    def reconfirm(self, attendee, dry_run):
        if dry_run:
            print('I would reconfirm:', attendee.user.username)
            return
        attendee.reconfirm = True
        attendee.save()

    def handle(self, *args, **options):
        if not settings.RECONFIRMATION:
            print('Set RECONFIRMATION=True and try again')
            return

        dry_run = not options['yes']
        if dry_run:
            print('Not actually doing anything without --yes')
        for attendee in Attendee.objects.filter(
                reconfirm=False, final_dates=True):
            if attendee.user.userprofile.is_registered():
                self.check_reconfirm(attendee, dry_run)
