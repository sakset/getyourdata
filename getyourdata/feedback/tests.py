from django.test import TestCase
from django.core.urlresolvers import reverse

from getyourdata.test import isDjangoTest, isSeleniumTest

from feedback.models import ServiceFeedback

# TODO tämä valmiiksi!!!
'''
@isDjangoTest()
class FeedbackTests(TestCase):

    def test_feedback_can_be_sent_if_valid_message_and_valid_captcha(self):
        response = self.client.post(
            reverse("feedback:send_feedback"),
            {"content": "valid test feedback message",
             "g-recaptcha-response": "PASSED"},
            follow=True)

        self.assertEquals(list(response.context['messages'])[0].message, "Thank you for your feedback!")
'''
