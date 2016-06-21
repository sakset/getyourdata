from django.test.runner import DiscoverRunner

from django.conf import settings

class TestSuiteRunner(DiscoverRunner):
    def setup_test_environment(self, *args, **kwargs):
        # Not an ideal solution; maybe the relevant methods
        # should be mocked instead
        settings.TESTING = True
        super(TestSuiteRunner, self).setup_test_environment(*args, **kwargs)
