from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver

import os
import sys


class LiveServerTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(LiveServerTestCase, cls).setUpClass()

        os.environ["SELENIUM_TESTS"] = 'True'

        cls.sauce_labs_active = False

        if os.environ.get("SAUCE_ACCESS_KEY", None):
            from sauceclient import SauceClient

            cls.sauce_labs_active = True

            # We are running tests using Sauce Labs
            cls.desired_capabilities = {}
            cls.desired_capabilities['tunnel-identifier'] = \
                os.environ['TRAVIS_JOB_NUMBER']
            cls.desired_capabilities['build'] = os.environ['TRAVIS_BUILD_NUMBER']
            cls.desired_capabilities['tags'] = \
                [os.environ['TRAVIS_PYTHON_VERSION'], 'CI']

            # Use Firefox 29 and Linux for Sauce Labs tests
            cls.desired_capabilities['platform'] = "Linux"
            cls.desired_capabilities['browserName'] = "firefox"
            cls.desired_capabilities['version'] = "29"

            USERNAME = os.environ.get("SAUCE_USERNAME")
            ACCESS_KEY = os.environ.get("SAUCE_ACCESS_KEY")

            cls.sauce = SauceClient(USERNAME, ACCESS_KEY)

            sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub"
            cls.selenium = webdriver.Remote(
                desired_capabilities=cls.desired_capabilities,
                command_executor=sauce_url % (USERNAME, ACCESS_KEY)
            )
            cls.selenium.implicitly_wait(10)
        else:
            # We are running test locally
            cls.selenium = WebDriver()
            # Prevent tests from failing by making the test wait longer
            # if element isn't immediately available
            cls.selenium.implicitly_wait(3)

    @classmethod
    def tearDownClass(cls):
        if cls.sauce_labs_active:
            try:
                if sys.exc_info() == (None, None, None):
                    cls.sauce.jobs.update_job(
                        cls.selenium.session_id, passed=True)
                else:
                    cls.sauce.jobs.update_job(
                        cls.selenium.session_id, passed=False)
            finally:
                cls.selenium.quit()
        else:
            cls.selenium.quit()

        super(LiveServerTestCase, cls).tearDownClass()
