from django.apps import AppConfig


class SseConfig(AppConfig):
    name = 'sse'

    def ready(self):
        from . import signals  # noqa: F401