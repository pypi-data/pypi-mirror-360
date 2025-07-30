import os
from django.core.management.base import BaseCommand
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from wafer.pages.models import Page


PAGES = [
    {
        "name": _("Home page"),
        "slug": "index",  # can't be translated
        "include_in_menu": False,
    },
    {
        "name": _("About"),
        "slug": _("about"),
        "include_in_menu": True,
        "children": [
            {
                "name": _("About the event"),
                "slug": _("event"),
                "include_in_menu": True,
            },
            {
                "name": _("Code of Conduct"),
                "slug": _("coc"),
                "include_in_menu": True,
            },
            {
                "name": _("Organizers"),
                "slug": _("org"),
                "include_in_menu": True,
            },
        ]
    },
    {
        "name": _("Contribute"),
        "slug": _("contribute"),
        "include_in_menu": True,
        "children": [
            {
                "name": _("Call for Proposals"),
                "slug": _("cfp"),
                "include_in_menu": True,
            },
            {
                "name": _("Important dates"),
                "slug": _("important-dates"),
                "include_in_menu": True,
            },
        ]
    },
    {
        "name": _("Schedule"),
        "slug": "schedule",  # can't be translated
        "include_in_menu": True,
    },
]


class Command(BaseCommand):
    help = 'Create sample set of pages for a MiniDebConf'

    def handle(self, *args, **options):
        if Page.objects.count():
            return
        self.create_pages(None, PAGES)

    def create_pages(self, parent, pages):
        for i, entry in enumerate(pages):
            entry["name"] = str(entry["name"])
            entry["slug"] = str(entry["slug"])
            self.create_page(menu_order=i, parent=parent, **entry)

    def create_page(self, **data):
        try:
            children = data.pop("children")
        except KeyError:
            children = []
        name = data["name"]
        content = f"# {name}\n\n"
        page = Page.objects.create(content=content, **data)
        print(f"Created page {page}")
        if children:
            self.create_pages(page, children)

