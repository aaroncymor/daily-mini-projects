import httpx
from typing import Any

from django.shortcuts import render
from django.conf import settings

from .forms import SearchForm, BacklogItemForm
from .models import BacklogItem


IN_MEMORY_CACHE = {}


# helpers
def cache_query_results(results: dict[str, Any], media_type: str) -> bool:

    if 'data' not in results:
        return False

    for res in results['data']:
        try:
            print(f"Searching for {str(res['malId'])} - {res['title']}")
            BacklogItem.objects.get(mal_id=res['malId'])
        except BacklogItem.DoesNotExist:
            print(f"Creating record: ({str(res['malId'])} - {res['title']})")
            episodes = res.get('episodes', 0)
            BacklogItem.objects.create(
                title=res['title'],
                mal_id=res['malId'],
                media_type=media_type,
                current_progress=0,
                total_units=episodes or 0
            )
    return True


def parse_db_results(db_results) -> list[dict[str, Any]]:
    return db_results.values('mal_id', 'title')


def parse_api_json(api_results: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    if 'data' in api_results:
        for res in api_results['data']:
            results.append({
                'id': res['malId'],
                'title': res['title'],
            })
    return results


# Create your views here.
def dashboard(request, *args, **kwargs):
    return render(
        request, 'backlog/dashboard.html', {
            'search_form': SearchForm()
    })


def search(request, *args, **kwargs):

    if request.POST:
        title = request.POST.get('title', '')

        if not title:
            return render(request, 'backlog/dashboard.html', {
                'search_form': SearchForm(),
                'search_results': []
            })

        if title in IN_MEMORY_CACHE:
            return render(request, 'backlog/dashboard.html', {
                'search_form': SearchForm({'title': title}),
                'search_results': IN_MEMORY_CACHE['title']
            })

        db_results = BacklogItem.objects.filter(
            title__icontains=title, media_type='anime'
        )

        # database caching
        if db_results.count() > 0:
            results = parse_db_results(db_results)
            IN_MEMORY_CACHE['title'] = results

            return render(
                request, 'backlog/dashboard.html', {
                    'search_form': SearchForm({
                        'title': title
                    }),
                    'search_results': list(results)
                }
            )

        # if not in the database, do api GET request
        response = httpx.get(f'{settings.JIKAN_BASE_URL}/anime?q={title}')
        if response:
            results = parse_api_json(response.json())
            IN_MEMORY_CACHE['title'] = results
            if cache_query_results(response.json(), 'anime'):
                return render(
                    request, 'backlog/dashboard.html', {
                        'search_form': SearchForm({
                            'title': title
                        }),
                        'search_results': results
                    }
                )

    return render(request, 'backlog/dashboard.html', {
        'search_form': SearchForm(),
        'search_results': []
    })


def get_backlog_item(request, mal_id, *args, **kwargs):

    try:
        backlog_item = BacklogItem.objects.get(mal_id=mal_id)

        return render(request, 'backlog/backlog_item_detail.html', {
            'backlog_item': backlog_item,
            'backlog_item_form': BacklogItemForm({
                'id': backlog_item.id,
                'title': backlog_item.title,
                'mal_id': backlog_item.mal_id,
                'media_type': backlog_item.media_type,
                'current_progress': backlog_item.current_progress,
                'total_units': backlog_item.total_units,
                'start_date': backlog_item.start_date,
                'target_date': backlog_item.target_date
            })
        })
    except BacklogItem.DoesNotExist:
        return render(request, 'backlog/backlog_item_detail.html', {
            'error': "Backlog item doesn't exist."
        })

    return render(request, 'backlog/backlog_item_detail.html', {
        'error': "Unknown error occured."
    })


def update_backlog_item(request, mal_id, *args, **kwargs):
    if request.POST:
        try:
            backlog_item = BacklogItem.objects.get(mal_id=mal_id)
            id = request.POST.get('id')
            mal_id = request.POST.get('mal_id')
            title = request.POST.get('title', '')
            media_type = request.POST.get('media_type', 'anime')
            current_progress = request.POST.get('current_progress', 0)
            total_units = request.POST.get('total_units', 0)
            start_date = request.POST.get('start_date')
            target_date = request.POST.get('target_date')

            print("id", id)
            print("mal_id", mal_id)
            print("title", title)
            print("media_type", media_type)
            print("current_progress", current_progress)
            print("total_units", total_units)
            print("start_date", start_date)
            print("target_date", target_date)


            return render(request, 'backlog/backlog_item_detail.html', {
                'backlog_item': backlog_item,
                'backlog_item_form': BacklogItemForm({
                    'id': id,
                    'mal_id': mal_id,
                    'title': title,
                    'media_type': media_type,
                    'current_progress': current_progress,
                    'total_units': total_units,
                    'start_date': start_date,
                    'target_date': target_date
                }),
            })
        except BacklogItem.DoesNotExist:
            return render(request, 'backlog/backlog_item_detail.html', {
                'backlog_item_form': BacklogItemForm(),
                'error': "Backlog item doesn't exist."
            })

    return render(request, 'backlog/backlog_item_detail.html', {
        'backlog_item_form': BacklogItemForm(),
    })
