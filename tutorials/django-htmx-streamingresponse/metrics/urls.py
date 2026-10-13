from django.urls import path

from . import views

app_name = "metrics"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("sales/table/", views.sales_table, name="sales_table"),
    path("sales/<int:pk>/edit/", views.edit_row, name="edit_row"),
    path("activity/stream/", views.activity_stream, name="activity_stream"),
]
