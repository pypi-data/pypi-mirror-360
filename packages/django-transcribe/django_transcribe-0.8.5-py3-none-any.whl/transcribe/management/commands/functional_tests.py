"""Add permissions for proxy model.

This is needed because of the bug https://code.djangoproject.com/ticket/11154
in Django (as of 1.6, it's not fixed).

When a permission is created for a proxy model, it actually creates if for it's
base model app_label (eg: for "article" instead of "about", for the About proxy
model).

What we need, however, is that the permission be created for the proxy model
itself, in order to have the proper entries displayed in the admin.

From gist: https://gist.github.com/magopian/7543724

"""
import os
import subprocess

from django.core.management.commands import test
from functional_tests import shared

BROWSERS = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'IE']
USE_XVFB = ['Firefox', 'Safari', 'Edge', 'IE']


class Command(test.Command):
    help = 'Run functional tests.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--browser', '-b', choices=BROWSERS, default='Chrome'
        )
        parser.add_argument('--gui', '-g', action='store_true', dest='gui')
        parser.add_argument('--display', '-x', default=':10')
        super().add_arguments(parser)

    def handle(self, *test_labels, browser, gui, display, **options):
        shared.browser_type = browser
        shared.force_gui = gui
        if browser in USE_XVFB and not gui:
            xvfb = subprocess.Popen(['Xvfb', display])
            os.environ['DISPLAY'] = display
        if not test_labels:
            test_labels = ['functional_tests']
        super().handle(*test_labels, **options)
        try:
            xvfb.kill()
        except UnboundLocalError:
            pass
