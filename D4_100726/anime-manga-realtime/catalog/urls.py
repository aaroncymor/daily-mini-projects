from django.urls import path

from . import views


urlpatterns = [
    path("", views.catalog_index, name="catalog_index"),
    path("search/", views.catalog_search, name="catalog_search"),
    path("list/", views.catalog_list, name="catalog_list"),
    path("<int:pk>/", views.catalog_detail, name="catalog_detail"),
]
