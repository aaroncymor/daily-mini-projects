from django.shortcuts import render

from .models import Excerpt
from .helpers import search_philosophers, get_random_quote


# Create your views here.
def excerpt_search(request, *args, **kwargs):
    """
    Search excerpts by philosopher
    """

    if request.POST:
        author = request.POST.get('author')
        philosophers = search_philosophers(author)

        print("Philosophers", philosophers)
        return render(
            request, 'philosophy/index.html#philosopher_list',
            {"philosophers": philosophers}
        )


def philosophy_index(request, *args, **kwargs):
    return render(request, 'philosophy/index.html', {})


def quote_random(request, *args, **kwargs):
    pass


def excerpt_import(request, *args, **kwargs):
    pass


def excerpt_compare(request, *args, **kwargs):
    pass
