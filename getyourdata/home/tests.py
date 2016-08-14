from django.test import TestCase
from django.core.urlresolvers import reverse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By

from getyourdata.test import isDjangoTest, isSeleniumTest
from getyourdata.testcase import LiveServerTestCase

from home.models import HomePage, FaqContent


@isDjangoTest()
class HomePageTests(TestCase):

    def test_homepage_has_content(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Get a copy of your own data")

    def test_only_one_homepage_is_automatically_created(self):
        self.assertEquals(HomePage.objects.all().count(), 0)
        response = self.client.get(reverse('home'))
        self.assertEquals(HomePage.objects.all().count(), 1)
        response = self.client.get(reverse('home'))
        self.assertEquals(HomePage.objects.all().count(), 1)


@isSeleniumTest()
class FaqsValidationTests(LiveServerTestCase):
    def setUp(self):
        self.data_requests = FaqContent.objects.create(
            title='testtitle',
            content='testcontent',
            priority='1',
        )
        self.data_requests = FaqContent.objects.create(
            title='othertitle',
            content='longer content with spaces',
            priority='10',
        )

        self.data_requests = FaqContent.objects.create(
            title='somethingelse',
            content='last, but not least',
            priority='5',
        )

    def test_selenium_faqs_can_be_seen_in_faq_view(self):
        self.selenium.get("%s%s" % (self.live_server_url,
                                    reverse("faq")))

        self.assertIn("testtitle", self.selenium.page_source)
        self.assertIn("testcontent", self.selenium.page_source)
        self.assertIn("othertitle", self.selenium.page_source)
        self.assertIn("longer content with spaces", self.selenium.page_source)
        self.assertIn("somethingelse", self.selenium.page_source)
        self.assertIn("last, but not least", self.selenium.page_source)

    def test_selenium_faqs_order_can_be_prioritized(self):
        self.selenium.get("%s%s" % (self.live_server_url,
                                    reverse("faq")))

        accordion = self.selenium.find_element_by_id("accordion")
        faqs = accordion.find_elements_by_class_name("panel-title")

        self.assertIn("testtitle", faqs[0].text)
        self.assertIn("othertitle", faqs[2].text)
        self.assertIn("somethingelse", faqs[1].text)
