from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("stream/", views.kuji_stream, name="kuji_stream"),
]