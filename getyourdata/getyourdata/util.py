"""A few utility methods that disable and enable transactions

They are used to keep saved requests for the duration of the test
so that they can be inspected

These methods should probably be mocked instead of relying on a setting value
"""

from django.db import transaction
from django.conf import settings


def set_autocommit_on():
    if not settings.TESTING:
        transaction.set_autocommit(True)


def rollback():
    if not settings.TESTING:
        transaction.rollback()


def set_autocommit_off():
    if not settings.TESTING:
        transaction.set_autocommit(False)
