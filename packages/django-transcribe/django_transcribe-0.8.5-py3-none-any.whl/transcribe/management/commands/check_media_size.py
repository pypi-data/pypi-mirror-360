import os

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from transcribe import settings


class Command(BaseCommand):
    help = (
        'Checks the size of the media directory and notify when limit is '
        'reached.'
    )

    def get_size(self, path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
            for directory in dirnames:
                total_size += self.get_size(directory)
        return total_size / 1_000_000_000.0  # bytes to GB

    def handle(self, *args, **options):
        try:
            limit = float(args[0])  # limit in GB
        except IndexError:
            limit = 5.0  # limit in GB
        media_dir = os.path.join(django_settings.MEDIA_ROOT, 'project_content')
        size = self.get_size(media_dir)
        print('Media dir is {:.2f}GB'.format(size))
        if size >= limit:
            subject = 'Transcribe Limit Reached!'
            msg = """
            The size of the media root (images for all projects) has passed the
            desired limit ({limit:.2f}GB). The current size is {size:.2f}GB.
            """.format(
                limit=limit, size=size
            )
            from_email = settings.FROM_EMAIL
            to_emails = [settings.SUPPORT_EMAIL]
            send_mail(subject, msg, from_email, to_emails)
