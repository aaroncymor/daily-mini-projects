from django.shortcuts import render

from django.conf import settings
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import ANIME_CHOICE, MANGA_CHOICE, Catalog
from .helpers import search


# Create your views here.
def catalog_search(request, *args, **kwargs):
    if request.POST:
        title = request.POST.get('t')
        category = request.POST.get('c', ANIME_CHOICE)
        page_num = request.POST.get('page', 1)
        show = request.POST.get('show')

        if category not in (ANIME_CHOICE, MANGA_CHOICE):
            return render(
                request, 'catalog/index.html#search_items', {
                "error": "Category not supported.",
                "catalog_search": {}
            })
        query = {"category": category}

        if not title:
            return render(
                request, 'catalog/index.html#search_items', {
                "error": "Empty title not allowed.",
                "catalog_search": {}
            })
        query["title__icontains"] = title

        if show not in settings.SHOW_NUM_ITEMS:
            return render(
                request, 'catalog/index.html#search_items', {
                    "error": "Only show number of items allowed: 10, 25, 50, 100",
                "catalog_search": {}
            })

        if page_num:
            query["page"] = page_num

        catalogs = Catalog.objects.filter(**query)
        paginator = Paginator(catalogs, show)

        page_obj = paginator.get_page(page_num)

        return render(
            request, 'catalog/index.html#search_items',
            {"catalog_search": page_obj}
        )

    return HttpResponse(status=400)


def catalog_list(request, *args, **kwargs):
    if request.GET:
        category = request.GET.get('c', ANIME_CHOICE)
        page_num = request.GET.get('page', 1)
        show = request.GET.get('show', 10)

        catalogs = Catalog.objects.filter(category=category).order_by("title")

        paginator = Paginator(catalogs, show)
        page_obj = paginator.get_page(page_num)
        return render(request, 'catalog/partials/list.html', {
            'catalog_items': page_obj,
            'page_obj': page_obj,
        })
    return render(request, 'catalog/index.html', {})


def catalog_detail(request, pk, *args, **kwargs):
    catalog_item = Catalog.objects.get(pk=pk)
    return render(request, 'catalog/partials/list.html#catalog_item', {
        "catalog_item": catalog_item
    })


def catalog_index(request, *args, **kwargs):
    catalogs = Catalog.objects.filter(category=ANIME_CHOICE).order_by("title")
    paginator = Paginator(catalogs, 10)
    page_obj = paginator.get_page(1)
    return render(request, 'catalog/index.html', {'catalog_items': page_obj})
