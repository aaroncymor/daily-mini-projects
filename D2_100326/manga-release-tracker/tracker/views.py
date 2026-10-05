import json

from django.shortcuts import render
from django.http import HttpResponse

from .models import MangaSubscription, NotificationLog
from .helpers import search

# IN_MEMORY_CACHE = {}


# Create your views here.
def manga_search(request, *args, **kwargs):
    if request.POST:
        try:
            title = request.POST.get('title', '')
            search_results = [] if not title else search(title)
            return render(
                request,
                'tracker/partials/search_results.html',
                context={'search_results': search_results}
            )
        except Exception:
            return render(
                request,
                'tracker/partials/search_results.html',
                context={'error': 'An error occured while making request to the server.'}
            )
    return HttpResponse(status=400)


def manga_subscribe(request, manga_id, *args, **kwargs):
    if request.POST:
        manga_sub = MangaSubscription.objects.get(manga_id=manga_id)
        subscribe = request.POST.get("subscribe")

        manga_sub.is_subscribed = True if subscribe == "true" else False
        manga_sub.save()

        # If request originated from inside #subscribedManga, return
        # the updated subscribed list
        if request.META.get('HTTP_HX_TARGET', '') == "subscribedManga":
            manga_subs = MangaSubscription.objects.filter(is_subscribed=True)
            response = render(
                request,
                "tracker/partials/subscribed_list.html",
                {"manga_subs": manga_subs}
            )
        else:
            # default response for search result item
            response = render(
                request,
                'tracker/partials/search_results.html#manga-item',
                context={"res": manga_sub, "manga_sub": manga_sub}
            )

        # response['HX-Trigger'] = 'mangaSubscribed'
        response['HX-Trigger'] = json.dumps({'mangaSubscribed': {"target": "body"}})
        return response

    return HttpResponse(status=400)


def manga_list(request, *args, **kwargs):
    manga_subs = MangaSubscription.objects.filter(is_subscribed=True)
    notifs = NotificationLog.objects.all().order_by("-sent_at")
    return render(request, "tracker/index.html", {
        "manga_subs": manga_subs, "notifs": notifs
    })


def subscribed_manga_list(request, *args, **kwargs):
    manga_subs = MangaSubscription.objects.filter(is_subscribed=True)
    return render(
        request,
        "tracker/partials/subscribed_list.html",
        {"manga_subs": manga_subs}
    )
