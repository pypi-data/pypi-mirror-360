import os
from pathlib import Path

try:
    from django.conf import settings
except ImportError:
    settings = None

transcribe_settings = getattr(settings, 'TRANSCRIBE_SETTINGS', {})


def get_conf(key, default=None):
    """Safely gets configuration option from settings."""
    return transcribe_settings.get(key, default)


BASE_DIR = Path(getattr(settings, 'BASE_DIR', os.getcwd()))
SUPPORT_EMAIL = get_conf('support_email', 'something@example.com')
FROM_EMAIL = get_conf('from_email', 'no_reply@example.com')
TASK_EXPIRE_DAYS = get_conf('task_expire_days', 14)
