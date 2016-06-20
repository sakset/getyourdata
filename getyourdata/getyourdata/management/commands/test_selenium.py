from django.core.management import call_command
from django.core.management.base import BaseCommand

import os

class Command(BaseCommand):
    help = 'Run only Selenium tests'

    def handle(self, *args, **kwargs):
        os.environ["RUN_SELENIUM_TESTS"] = "true"
        os.environ["SKIP_DJANGO_TESTS"] = "true"

        call_command("test", *args, **kwargs)
