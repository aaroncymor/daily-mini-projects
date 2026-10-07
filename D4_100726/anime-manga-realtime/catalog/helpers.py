from typing import Any, Optional

import httpx

from django.conf import settings

from .models import (
    ANIME_CHOICE, MANGA_CHOICE, Catalog
)


def get_animes_or_mangas(
        category: str, keyword: str, page: Optional[str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:

    if category not in (ANIME_CHOICE, MANGA_CHOICE):
        raise ValueError(f"Invalid category: {category}.")

    url = f"{settings.JIKAN_BASE_URL}/{category}?q={keyword}"
    if page:
        url += f"&page={page}"

    response = httpx.get(url)
    if response.status_code != 200:
        raise Exception("Request to API server failed.")

    results: dict[str, Any] = response.json()
    if not (
        type(results) == dict and 'data' in results and 'meta' in results
    ):
        raise Exception(f"Response data changed for url: {url}.")

    return results['data'], results['meta']


def parse_and_save_results(
    category: str, data: list[dict[str, Any]], meta_data: dict[str, Any]
):
    for item in data:
        episodes_volumes = "episodes" if "episodes" in item else "volumes"

        instance, created = Catalog.get_or_create(
            mal_id=item.get('malId'),
            defaults={
                'malId': item.get('malId'),
                'url': item.get('url', ''),
                'title': item.get('title', ''),
                'image_url': item.get('imageUrl', ''),
                'description': item.get('synopsis', ''),
                'category': category,
                'catalog_type': item.get('type', ''),
                'score': item.get('score', 0.0),
                'episodes_volumes': item.get(episodes_volumes, 0)
            }
        )
        if created:
            print(f"Successfully created: {item.get('title')};{category}")
        else:
            print(f"Item already exists: {item.get('title')};{category}")

        # save in memory here...
        # ... redis.set(key, value)


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
