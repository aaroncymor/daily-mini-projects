import httpx
from typing import Any, List

from django.shortcuts import render
from django.conf import settings

from .forms import SearchForm
from .models import BacklogItem


IN_MEMORY_CACHE = {}


## helpers
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


def parse_db_results(db_results) -> List[str]:
    lst = db_results.values_list('title', flat=True)
    return lst


def parse_api_json(api_results: dict[str, Any]) -> List[str]:
    results = []
    if 'data' in api_results:
        for res in api_results['data']:
            results.append(res['title'])
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
