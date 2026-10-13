from django.urls import path
from .views import sse_progress_stream, index


urlpatterns = [
    path('', index, name='realtime_index'),
    path('stream/', sse_progress_stream, name='realtime_stream'),
]
