from django.shortcuts import render

from django.http import HttpResponse
from .helpers import search


# Create your views here.
def catalog_search(request, *args, **kwargs):
    pass


def catalog_index(request, *args, **kwargs):
    if request.POST:
        category = request.POST.get('category')
        title = request.POST.get('title')

        search_results = search(category, title)
        return render(request, 'catalog/index.html', {
            "search_results": search_results
        })

    return HttpResponse(status=400)
