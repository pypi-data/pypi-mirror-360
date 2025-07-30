import re
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

import requests


class Command(BaseCommand):
    help = "Retry previously failed mailing list subscriptions"
    subscribed = {}

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true',
                            help='Actually do something')
        parser.add_argument('--since', type=parse_datetime, metavar='TIMESTAMP',
                            default=datetime(2000, 1, 1),
                            help='Skip log entries before TIMESTAMP')
        parser.add_argument("--timeout", type=int,
                            default=5,
                            help="Timeout waiting for lists.debian.org")
        parser.add_argument('log', type=open,
                            help='Log file to search for failed subscriptions')

    def subscribe(self, address, lists, timeout):
        if set(lists) <= self.subscribed.get(address, set()):
            return
        try:
            requests.post(
                'https://lists.debian.org/cgi-bin/subscribe.pl',
                data={
                    'user_email': address,
                    'subscribe': lists,
                },
                timeout=timeout,
            )
        except requests.Timeout:
            print(f"Failed to subscribe {address} to {lists}")
        self.subscribed.setdefault(address, set()).update(set(lists))

    def handle(self, *args, **options):
        for line in options['log']:
            if m := re.match(
                    r'(^[0-9: -]{19}),\d+\s+INFO\s+register.views.attendee '
                    r'Failed to subscribe (\S+) to \[([a-z\', -]+)\]$',
                    line.strip()):
                timestamp = m.group(1)
                if parse_datetime(timestamp) < options['since']:
                    continue

                address = m.group(2)
                lists = [list.strip("' ") for list in m.group(3).split(',')]
                if not options['yes']:
                    print(f"Would subscribe {address} to {lists}")
                else:
                    self.subscribe(address, lists, options['timeout'])
