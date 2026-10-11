from django.shortcuts import render

from django.conf import settings
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import ANIME_CHOICE, MANGA_CHOICE, Catalog
from .helpers import search


# Create your views here.
def catalog_search(request, *args, **kwargs):
    if request.POST:
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', ANIME_CHOICE)
        try:
            show = int(request.POST.get('show', 10))
        except (ValueError, TypeError):
            show = 10

        query = {"category": category}
        if title:
            query['title__icontains'] = title
        catalogs = Catalog.objects.filter(**query).order_by("title")

        paginator = Paginator(catalogs, show)
        page_obj = paginator.get_page(1)

        return render(
            request, 'catalog/partials/list.html',
            {
                "catalog_items": page_obj,
                "page_obj": page_obj
            })

    return HttpResponse(status=400)


def catalog_list(request, *args, **kwargs):
    title = request.GET.get('title', '')
    category = request.GET.get('category', ANIME_CHOICE)
    page_num = request.GET.get('page', 1)

    try:
        show = int(request.GET.get('show', 10))
    except (ValueError, TypeError):
        show = 10

    query = {"category": category}
    if title:
        query['title__icontains'] = title

    catalogs = Catalog.objects.filter(**query).order_by("title")
    paginator = Paginator(catalogs, show)
    page_obj = paginator.get_page(page_num)

    context = {
        'catalog_items': page_obj, 'page_obj': page_obj
    }
    # if requested via htmx, return partial
    if request.htmx:
        return render(request, 'catalog/partials/list.html', context)

    return render(request, 'catalog/index.html', context)


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
