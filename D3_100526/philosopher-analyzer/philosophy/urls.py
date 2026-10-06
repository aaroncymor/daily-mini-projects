from django.urls import path

from . import views


urlpatterns = [
    path('', views.philosophy_index, name="philosophy_index"),
    path('search', views.excerpt_search, name="excerpt_search"),
]
