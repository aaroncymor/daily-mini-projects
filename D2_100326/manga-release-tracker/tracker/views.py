import httpx

from typing import Any

from django.shortcuts import render
from django.conf import settings

from .models import MangaSubscription

IN_MEMORY_CACHE = {}


# helpers
def parse_and_save_results(response: dict[str, Any]):
    """
    Go through list of api response from MangaDex and save to database
    if manga does not exist.
    """

    if 'data' not in response:
        print("Access response['data'] failed.")
        return

    data = response['data']

    res = []
    for manga in data:

        manga_id = data.get('id')
        title = data.get("title")
        status = data.get("status")

        manga_info = {
            'manga_id': manga_id,
            'title': title,
            'status': status
        }

        try:
            manga_subscription = MangaSubscription.objects.get(
                manga_id=manga_info['manga_id']
            )
        except MangaSubscription.DoesNotExist:
            # create record if does not exist
            MangaSubscription.objects.create(manga_info)

        res.append(manga_info)

    return res


def search(title: str) -> list[dict[str, Any]]:
    """
    Searches for manga based on passed title in the cache.
    If not exists on cache, then checks database, if not on database
    then submit a request to mangadex api. Save the results
    """

    # check in cache first
    if title in IN_MEMORY_CACHE:
        return IN_MEMORY_CACHE[title]

    # if not in memory cache, query database
    db_results = MangaSubscription.objects.filter(title__icontains=title)
    if db_results.count() > 0:
        res = list(db_results.values('manga_id', 'title', 'status'))
        IN_MEMORY_CACHE[title] = res
        return res

    # if not in database, request third party api
    response = httpx.get(f'{settings.MANGADEX_BASE_URL}/manga?title={title}')
    if response.status_code != 200:
        raise Exception("Request to MangaDex server failed.")

    res = parse_and_save_results(response.json())
    IN_MEMORY_CACHE[title] = res
    return res


# Create your views here.
def search_manga(request, *args, **kwargs):

    if request.POST:
        try:
            query = request.POST.get('query')
            results = search(query)
            return render('', context={'search_results': results})
        except Exception:
            return render('', context={'errors': 'Manga does not exist'})

    return render('', context={'errors': "Unsupported error occured."})


def subscribe_manga(request, manga_id, *args, **kwargs):
    if request.POST:
        try:
            manga_subscription = MangaSubscription.objects.get(manga_id=manga_id)
            subscribe = request.POST.get("subscribe")

            manga_subscription.is_subscribed = subscribe
            manga_subscription.save()

            manga_subscription.refresh_from_db()

            return render('', context={})
        except Exception:
            return render('', context={'errors': 'Manga does not exist'})

    return render('', context={'errors': "Unsupported error occured."})


def list_manga(request, *args, **kwargs):
    if request.GET:
        manga_subscriptions = MangaSubscription.objects.filter(is_subscribed=True)

    return render('', context={'errors': "Unsupported error occured."})
