import httpx
from typing import Any
from django.conf import settings

from .models import MangaSubscription


def get_latest_chapter(manga_id: str) -> str:

    response = httpx.get(f"{settings.MANGADEX_BASE_URL}/manga/{manga_id}/aggregate")
    if response.status_code != 200:
        raise Exception(f"An error occured trying to get aggregate data from {manga_id}")
    volumes = response.json().get('volumes')
    if not volumes:
        return "none"
    return max(volumes.keys(), key=lambda k: float(k) if k not in ("", "none") else -1)


def parse_and_save_results(response: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Go through list of api response from MangaDex and save to database
    if manga does not exist.
    """

    if 'data' not in response:
        print("Access response['data'] failed.")
        return []

    data = response['data']

    res = []
    for manga in data:

        manga_id = manga.get('id')
        attributes = manga.get("attributes")
        alt_titles = attributes.get("altTitles")
        status = attributes.get("status")

        en_title = ""
        for alt_title in alt_titles:
            if "en" in alt_title:
                en_title = alt_title.get("en")

        if not en_title:
            print(f"Skipping {manga_id}; no english title...")
            continue

        manga_info = {
            'manga_id': manga_id,
            'title': en_title,
            'status': status,
            'is_subscribed': False,
        }

        print("MANGA INFO", manga_info)
        try:
            print(f"Searching for manga with {manga_info['manga_id']}...")
            manga_sub = MangaSubscription.objects.get(
                manga_id=manga_info['manga_id']
            )
            manga_info['is_subscribed'] = manga_sub.is_subscribed
            manga_info['current_chapter'] = manga_sub.current_chapter
        except MangaSubscription.DoesNotExist:
            # create record if does not exist
            print(f"Creating record for manga with {manga_info['manga_id']}...")

            # temporarily convert to UUID
            manga_info['current_chapter'] = get_latest_chapter(manga_id)
            # manga_info['manga_id'] = uuid.UUID(manga_info['manga_id'])
            MangaSubscription.objects.create(**manga_info)
            # manga_info['manga_id'] = str(manga_info['manga_id'])

        res.append(manga_info)

        print("RES", res)
    return res


def search(title: str) -> list[dict[str, Any]]:
    """
    Searches for manga based on passed title in the cache.
    If not exists on cache, then checks database, if not on database
    then submit a request to mangadex api. Save the results
    """

    # check in cache first
    # if title in IN_MEMORY_CACHE:
    #     return IN_MEMORY_CACHE[title]

    # if not in memory cache, query database
    db_results = MangaSubscription.objects.filter(title__icontains=title)
    print("DB RESULTS", db_results)
    if db_results.count() > 0:
        manga_subs = db_results.values(
            'manga_id', 'title', 'status',
            'current_chapter', 'is_subscribed',
        )

        res = [{
            "manga_id": str(manga_sub["manga_id"]),
            "title": manga_sub["title"],
            "status": manga_sub["status"],
            "current_chapter": manga_sub["current_chapter"],
            "is_subscribed": manga_sub["is_subscribed"]
        } for manga_sub in manga_subs]

        # IN_MEMORY_CACHE[title] = res
        return res

    # if not in database, request third party api
    response = httpx.get(f'{settings.MANGADEX_BASE_URL}/manga?title={title}')
    print("RESPONSE", response)
    if response.status_code != 200:
        raise Exception("Request to MangaDex server failed.")

    print("PARSING AND SAVING RESULTS...")
    res = parse_and_save_results(response.json())
    print("RES", res)
    # IN_MEMORY_CACHE[title] = res
    return res

