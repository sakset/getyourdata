from django.test.runner import DiscoverRunner

from django.conf import settings

import os


class TestSuiteRunner(DiscoverRunner):
    def setup_test_environment(self, *args, **kwargs):
        # Not an ideal solution; maybe the relevant methods
        # should be mocked instead
        settings.TESTING = True
        os.environ['RECAPTCHA_TESTING'] = 'True'
        super(TestSuiteRunner, self).setup_test_environment(*args, **kwargs)
