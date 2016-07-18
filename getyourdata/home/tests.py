from django.test import TestCase
from django.core.urlresolvers import reverse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By

from getyourdata.test import isDjangoTest, isSeleniumTest
from home.models import HomePage


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