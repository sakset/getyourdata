from unittest import skip

import os


def _id(obj):
    return obj


def isDjangoTest():
    """
    Mark TestCase as containing Django tests for 'test' and 'test_all'
    """
    if os.environ.get("SKIP_DJANGO_TESTS", False):
        return skip("Use 'test' or 'test_all' to run Django tests")
    return _id


def isSeleniumTest():
    """
    Mark TestCase as containing Selenium tests for 'test_selenium' and
    'test_all'
    """
    if not os.environ.get("RUN_SELENIUM_TESTS", False):
        return skip("Use 'test_selenium' or 'test_all' to run Selenium tests")
    return _id
