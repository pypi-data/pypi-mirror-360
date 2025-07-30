# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from invoices.prices import invoice_user


class Command(BaseCommand):
    help = 'Create an invoice for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', help='The user to invoice')
        parser.add_argument('--dry-run', action='store_true',
            help="Print the invoice we would create, without creating it.")

    def handle(self, *args, **options):
        username = options['username']
        dry_run = options['dry_run']
        User = get_user_model()
        user = User.objects.get(username=username)
        invoice = invoice_user(user, save=not dry_run)
        print(invoice)
