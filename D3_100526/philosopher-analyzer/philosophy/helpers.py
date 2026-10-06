import httpx
import textstat

from typing import Any

from django.db.models import Case, ExpressionWrapper, F, FloatField, Value, When
from django.conf import settings

from .models import Philosopher, Excerpt


def parse_and_save_results(
    search_results: list[dict[str, Any]]
) -> list[dict[str, Any]]:

    results = []
    for result in search_results:
        name = result.get('wikiTitle', "")
        philosopher_id = result.get("id", "")

        philo_obj = {"name": name, "philosopher_id": philosopher_id}

        if not name or not philosopher_id:
            continue

        print("Creating philosopher...", name, philosopher_id)
        philosopher, created = Philosopher.objects.get_or_create(
            philosopher_id=philosopher_id,
            defaults=philo_obj
        )
        if created:
            print("Philosopher successfully CREATED")

        response = httpx.get(
            f"{settings.PHILOSOPHERSAPI_BASE_URL}/api/philosophers/{philosopher_id}"
        )
        if response.status_code != 200:
            print(f"Extracting quotes from {name}-{philosopher_id} failed.")
            continue

        philo_obj['excerpts'] = []

        quotes = response.json().get('quotes')
        for quote_obj in quotes:
            title_of_work = quote_obj.get("work")
            quote = quote_obj.get("quote", "")
            quote_id = quote_obj.get("id")

            if not quote:
                print(f"No quote for work {title_of_work}")
                continue

            total_words = textstat.lexicon_count(
                quote, removepunct=True
            )

            words_list = quote.lower().split()
            unique_words = set(words_list)
            print("Creating excerpt...", quote_id)
            excerpt, created = Excerpt.objects.get_or_create(
                quote_id=quote_id,
                defaults={
                    "quote_id": quote_id,
                    "philosopher": philosopher,
                    "quote": quote,
                    "title_of_work": title_of_work,
                    "unique_words": len(unique_words),
                    "total_words": total_words,
                }
            )
            if created:
                print("Excerpt successfully CREATED!")

            philo_obj['excerpts'].append({
                "quote_id": quote_id,
                "quote": quote,
                "title_of_work": title_of_work,
                "unique_words": len(unique_words),
                "total_words": total_words,
                "lexical_density": excerpt.lexical_density,
            })
        results.append(philo_obj)
    return results


def search_philosophers(author: str):

    philosophers = Philosopher.objects.filter(name__icontains=author)
    results = []
    if philosophers.count() > 0:
        for philosopher in philosophers:

            philo_obj = {
                "name": philosopher.name,
                "philosopher_id": philosopher.philosopher_id
            }

            excerpts = philosopher.excerpts.annotate(
                lexical_density=Case(
                    When(total_words=0, then=Value(None)),
                    When(total_words__isnull=True, then=Value(None)),
                    default=ExpressionWrapper(
                        F('unique_words') * 1.0 / F('total_words'),
                        output_field=FloatField()
                    ),
                    output_field=FloatField()
                )
            ).values(
                'quote_id', 'quote', 'title_of_work',
                'unique_words', 'total_words', 'lexical_density'
            )
            philo_obj['excerpts'] = excerpts

            results.append(philo_obj)
        return results

    response = httpx.get(f"{settings.PHILOSOPHERSAPI_BASE_URL}/api/philosophers/search?keyword={author}")
    if response.status_code != 200:
        raise Exception("An error occured trying to request to Third Party API.")

    return parse_and_save_results(response.json())


def get_random_quote(philosopher_id):
    pass
