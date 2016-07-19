#coding:utf-8
from django.test import TestCase
from django.core.urlresolvers import reverse

from getyourdata.test import isDjangoTest

from feedback.models import ServiceFeedback

from random import choice
from string import ascii_letters


@isDjangoTest()
class FeedbackTests(TestCase):
    def test_feedback_can_be_sent_if_valid_message(self):
        success_message = "Thank you for your feedback!"
        test_feedback = ''.join(choice(ascii_letters) for i in range(256))

        response = self.client.post(
            reverse("feedback:send_feedback"),
            {"content": test_feedback},
            follow=True)

        self.assertEquals(
            ServiceFeedback.objects.all()[0].content, test_feedback)
        self.assertEquals(
            list(response.context['messages'])[0].message, success_message)

    def test_feedback_cannot_be_sent_if_too_long_message(self):
        test_feedback = ''.join(choice(ascii_letters) for i in range(4097))

        response = self.client.post(
            reverse("feedback:send_feedback"), {"content": test_feedback},
            follow=True)

        saved_feedback_count = len(ServiceFeedback.objects.all())

        self.assertEquals(saved_feedback_count, 0)
        self.assertEquals(
            list(response.context['messages'])[0].message,
            "Message: Maximum allowed length is 4096 characters")
