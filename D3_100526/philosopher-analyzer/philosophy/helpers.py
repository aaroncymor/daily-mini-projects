import httpx
import textstat

from typing import Any

from django.conf import settings
from .models import Excerpt


def parse_and_save_results(
    search_results: list[dict[str, Any]]
) -> list[dict[str, Any]]:

    res = []
    for result in search_results:
        author = result.get('wikiTitle', "")
        philosopher_id = result.get("id", "")

        if not author or not philosopher_id:
            continue

        response = httpx.get(
            f"{settings.PHILOSOPHERSAPI_BASE_URL}/api/philosophers/{philosopher_id}"
        )

        if response.status_code != 200:
            print(f"Extracting quotes from {author}-{philosopher_id} failed.")
            continue

        quotes = response.json().get('quotes')
        for quote_obj in quotes:
            work = quote_obj.get("work")

            quote = quote_obj.get("quote", "")
            if not quote:
                print(f"No quote for work {work}")
                continue

            total_words = textstat.lexicon_count(quote, removepunct=True)

            words_list = quote.lower().split()
            unique_words = set(words_list)

            _excerpt = {
                "philosopher_id": philosopher_id,
                "author": author,
                "title_of_work": work,
                "quote": quote,
                "unique_words": unique_words,
                "total_words": total_words
            }

            Excerpt.objects.create(**_excerpt)
            res.append(_excerpt)
    return res



def search_philosopher(keyword: str):

    db_results = Excerpt.objects.filter(author__icontains=keyword)
    if db_results.count() > 0:
        return list(
            db_results.values(
                'philosopher_id', 'author', 'quote',
                'unique_words', 'total_words'
            ))

    response = httpx.get(
        f"{settings.PHILOSOPHERSAPI_BASE_URL}/api/philosophers/search?keyword={keyword}"
    )

    if response.status_code != 200:
        raise Exception("An error occured trying to request to Third Party API.")

    return parse_and_save_results(response.json())


def get_random_quote(philosopher_id):
    pass
