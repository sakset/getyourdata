#coding:utf-8
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from getyourdata.test import isDjangoTest, isSeleniumTest
from getyourdata.testcase import LiveServerTestCase

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from feedback.models import ServiceFeedback
from feedback import services

from random import choice
from string import ascii_letters


@isDjangoTest()
class FeedbackTests(TestCase):
    def test_feedback_can_be_sent_if_valid_message(self):
        success_message = "Thank you for your feedback!"
        test_feedback = ''.join(choice(ascii_letters) for i in range(256))

        response = self.client.post(
            reverse("feedback:send_feedback"),
            {"content": test_feedback,
             "origin_url": "/en/"},
            follow=True)

        feedback = ServiceFeedback.objects.all()[0]

        self.assertEquals(feedback.content, test_feedback)
        self.assertEquals(feedback.origin_url, "/en/")

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

    def test_feedback_form_includes_current_url(self):
        response = self.client.get(
            reverse("organization:list_organizations"))

        self.assertContains(response, "value=\"/en/organizations/\"")

    def test_feedback_sent_to_slack_channel_only_if_enabled(self):
        # We've mocked the send_slack_message in test_monkeypatch.py
        # to track the amount of times it's called
        test_feedback = "This site is completely awful."

        services.send_slack_message.call_count = 0

        with self.settings(SLACK_WEBHOOK_ENABLED=True,
                           SLACK_WEBHOOK_URL="http://127.0.0.1"):
            response = self.client.post(
                reverse("feedback:send_feedback"), {"content": test_feedback},
                follow=True)

            self.assertEquals(services.send_slack_message.call_count, 1)

        with self.settings(SLACK_WEBHOOK_ENABLED=False,
                           SLACK_WEBHOOK_URL="http://127.0.0.1"):
            response = self.client.post(
                reverse("feedback:send_feedback"), {"content": test_feedback},
                follow=True)

            # It wasn't called, so the call count stays the same
            self.assertEquals(services.send_slack_message.call_count, 1)


@isSeleniumTest()
class FeedbackLiveTests(LiveServerTestCase):
    def test_user_can_send_feedback(self):
        self.selenium.get(
            "%s" % (self.live_server_url))

        self.selenium.find_element_by_id("give_feedback_nav_link").click()

        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "(//input[@id='send_feedback' and @disabled='disabled'])"))
        )

        self.selenium.find_element_by_id(
            "id_content").send_keys("This is feedback.")

        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "(//input[@id='send_feedback' and not(contains(@disabled, 'disabled'))])"))
        )

        self.selenium.find_element_by_id("send_feedback").click()

        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "(//form[@id='send_feedback_form']/div[@class='alert alert-success'])"))
        )

        self.assertIn("Thank you for your feedback!", self.selenium.page_source)
