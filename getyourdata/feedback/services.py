import requests

from django.conf import settings
from django.template.defaultfilters import truncatechars
from django.utils.translation import ugettext as _

import json


def send_slack_message(content, origin_url):
    """
    Send a message to a Slack channel using a webhook URL
    """
    payload = {
        "text": "%s:%s\n\n%s" % (
            _("The following feedback was sent:\n"),
            truncatechars(content, 800),
            "%s: %s" % (_("Originating URL"), origin_url))
    }

    try:
        requests.post(settings.SLACK_WEBHOOK_URL, data={
            'payload': json.dumps(payload)})
        return True
    except:
        return False
