from collections.abc import MutableMapping
from typing import Any, Optional

import httpx

from django.conf import settings

from .models import (
    ANIME_CHOICE, MANGA_CHOICE, Catalog
)


def memoize(key: str, value: Any):
    print(f"Memoizing {key}-{value.get('title')} pair...")


def get_animes_or_mangas(
    category: str, title: str, page: Optional[int] = 1
) -> tuple[list[dict[str, Any]], dict[str, Any]]:

    if category not in (ANIME_CHOICE, MANGA_CHOICE):
        raise ValueError(f"Invalid category: {category}.")

    url = f"{settings.JIKAN_BASE_URL}/{category}?q={title}"
    if page:
        url += f"&page={str(page)}"

    print(f"Requesting to {url}...")
    response = httpx.get(url)
    if response.status_code != 200:
        raise Exception("Request to API server failed.")

    result = response.json()

    if not (isinstance(result, MutableMapping) and 'data' in result):
        raise Exception(f"Response data changed for url: {url}.")

    for item in result.get('data', []):
        yield item

    # result['meta']['pagination']['hasNextPage']
    if not (
        'meta' in result and
        'pagination' in result.get('meta') and
        'hasNextPage' in result['meta'].get('pagination') and
        result['meta']['pagination']['hasNextPage']
    ):
        yield False
    else:
        yield True


def parse_and_save_data(category: str, item: dict[str, Any]):

    episodes_volumes = "episodes" if "episodes" in item else "volumes"
    defaults = {
        'mal_id': item.get('malId'),
        'url': item.get('url', ''),
        'title': item.get('title', ''),
        'image_url': item.get('imageUrl', ''),
        'description': item.get('synopsis', ''),
        'category': category,
        'catalog_type': item.get('type', ''),
        'score': item.get('score', 0.0),
        'episodes_volumes': item.get(episodes_volumes, 0)
    }
    instance, created = Catalog.objects.get_or_create(
        mal_id=item.get('malId'),
        defaults=defaults
    )

    if created:
        print(f"Successfully created: {item.get('title')};{category}")
    else:
        print(f"Item already exists: {item.get('title')};{category}")

    # save in memory here...
    # ... redis.set(key, value)
    memoize(item.get('malId'), defaults)


def search(category, title):

    catalogs = Catalog.objects.filter(
        title__icontains=title,
        category=category
    )

    catalogs.values(
        'title', 'mal_id', 'description', 'category',
        'catalog_type', 'score', 'episodes_volumes'
    )

    return catalogs
