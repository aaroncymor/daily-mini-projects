import time
from collections.abc import MutableMapping

from django.core.management.base import BaseCommand

from catalog.models import ANIME_CHOICE, MANGA_CHOICE
from catalog.helpers import get_animes_or_mangas, parse_and_save_data


class Command(BaseCommand):
    help = "Extracts anime and manga by name"

    def add_arguments(self, parser):
        parser.add_argument("category", type=str)
        parser.add_argument("title", type=str)

    def handle(self, *args, **options):
        category = options.get('category')
        title = options.get('title')

        print("CATEGORY", category, "TITLE", title)

        if category not in (ANIME_CHOICE, MANGA_CHOICE):
            raise ValueError('Invalid category used.')

        has_nxt_page = True
        page_num = 1

        while has_nxt_page and page_num > 0:
            for item in get_animes_or_mangas(category, title, page_num):

                if isinstance(item, bool):
                    has_nxt_page = item
                    page_num = page_num + 1 if has_nxt_page else -1
                    print("HAS NEXT PAGE", has_nxt_page, "PAGE NUM", page_num)

                if isinstance(item, MutableMapping):
                    parse_and_save_data(category, item)

            if has_nxt_page:
                print("Sleeping for 2s")
                time.sleep(2)



