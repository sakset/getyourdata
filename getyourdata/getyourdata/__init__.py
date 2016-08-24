from django.conf import settings

import feedback.services

if settings.TESTING:
    import getyourdata.test_monkeypatch
