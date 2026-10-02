from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('search/', views.search, name='search'),
    path(
        'item/<int:mal_id>/',
        views.get_backlog_item,
        name='get-backlog-item'
    ),
    path(
        'item/<int:mal_id>/update/',
        views.update_backlog_item,
        name='update-backlog-item'
    )
]
