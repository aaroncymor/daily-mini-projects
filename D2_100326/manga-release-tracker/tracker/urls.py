from django.urls import path
from . import views


urlpatterns = [
    path("", views.manga_list, name="manga_list"),
    path("subscribed-manga", views.subscribed_manga_list, name="subscribed_manga_list"),
    path("search", views.manga_search, name="manga_search"),
    path("<uuid:manga_id>/subscribe", views.manga_subscribe, name="manga_subscribe"),
]
