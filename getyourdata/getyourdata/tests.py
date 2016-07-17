from django.test import TestCase
from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import reverse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By

from getyourdata.test import isDjangoTest, isSeleniumTest


@isDjangoTest()
class FlatPageTests(TestCase):

    def setUp(self):
        flatpage = FlatPage.objects.create(
            title="Page",
            content="Content",
            url="/test-url/"
        )
        flatpage.sites.add(1)


    def test_flatpage_url_works(self):
        response = self.client.get("/en/test-url/")
        self.assertContains(response, "Content")
