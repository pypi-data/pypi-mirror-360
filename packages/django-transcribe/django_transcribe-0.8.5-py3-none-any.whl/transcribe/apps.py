import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class transcribeConfig(AppConfig):
    name = 'transcribe'
    verbose_name = 'transcribe'

    def ready(self):
        from . import signals  # noqa F401
