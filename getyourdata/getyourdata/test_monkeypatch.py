from django.conf import settings

import feedback.services

if settings.TESTING:
    # Monkey patch stuff since we're testing
    def mock_send_slack_message(content=None, origin_url=None):
        mock_send_slack_message.call_count += 1

    feedback.services.send_slack_message = mock_send_slack_message
    feedback.services.send_slack_message.call_count = 0
