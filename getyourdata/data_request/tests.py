import ipdb
from django.core.urlresolvers import reverse
from django.core import mail
from django.test import TestCase

from selenium.webdriver.firefox.webdriver import WebDriver

from getyourdata.test import isDjangoTest, isSeleniumTest
from getyourdata.testcase import LiveServerTestCase

from data_request.models import DataRequest, AuthenticationContent, FaqContent
from organization.models import Organization, AuthenticationField


def create_email_organization(test_case):
    email_organization = Organization.objects.create(
        name='Email organization',
        email_address='fake@address.com',
        address_line_one='Address one',
        address_line_two='Address two',
        postal_code='00000',
        country='Finland'
        )

    email_organization.authentication_fields.add(test_case.auth_field1)

    return email_organization


def create_mail_organization(test_case):
    mail_organization = Organization.objects.create(
        name='Mail organization',
        address_line_one='Address one',
        address_line_two='Address two',
        postal_code='00000',
        country='Finland'
        )

    mail_organization.authentication_fields.add(test_case.auth_field1)

    return mail_organization


@isDjangoTest()
class DataRequestCreationTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Organization',
            email_address='fake@address.com',
            address_line_one='Address one',
            address_line_two='Address two',
            postal_code='00000',
            country='Finland'
            )
        self.organization2 = Organization.objects.create(
            name='Organization Two',
            email_address='fake@addressa.com',
            address_line_one='Address 2',
            address_line_two='Address 4',
            postal_code='012345',
            country='Sweden'
            )

        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')
        self.auth_field2 = AuthenticationField.objects.create(
            name='other_thing',
            title="Other thing")
        self.auth_field3 = AuthenticationField.objects.create(
            name='oddest_thing',
            title="Oddest thing")

        self.assertEquals(self.organization.authentication_fields.all().count(), 0)

        self.organization.authentication_fields.add(self.auth_field1)
        self.organization.authentication_fields.add(self.auth_field2)

        self.organization2.authentication_fields.add(self.auth_field2)
        self.organization2.authentication_fields.add(self.auth_field3)

        self.assertEquals(self.organization.authentication_fields.all().count(), 2)
        self.assertEquals(self.organization2.authentication_fields.all().count(), 2)
        self.assertEquals(DataRequest.objects.all().count(), 0)
        self.assertEquals(AuthenticationContent.objects.all().count(), 0)

    def test_data_request_form_is_correct(self):
        response = self.client.get(reverse("data_request:request_data",
            args=(self.organization.id,)))

        self.assertContains(response, "Some number")
        self.assertContains(response, "Other thing")
        self.assertContains(response, "Request your data from Organization")

    def test_data_request_form_with_multiple_organizations_is_correct(self):
        response = self.client.get(
            reverse("data_request:request_data",
                    args=("%d,%d" % (self.organization.id,
                                     self.organization2.id),)))

        self.assertContains(response, "Some number")
        self.assertContains(response, "Other thing")
        self.assertContains(response, "Oddest thing")
        self.assertContains(response, "Request your data from multiple organizations")

    def test_data_request_is_created(self):
        self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"some_number": "1234567",
             "other_thing": "Some text here",
             "user_email_address": "test@test.com",
             "action": "send"},
            follow=True
            )

        self.assertEquals(DataRequest.objects.all().count(), 1)

        data_request = DataRequest.objects.first()

        self.assertTrue(data_request.organization == self.organization)

    def test_multiple_data_requests_can_be_created(self):
        self.client.post(
            reverse("data_request:request_data",
                    args=("%d,%d" % (self.organization.id,
                                     self.organization2.id),)),
            {"some_number": "1234567",
             "other_thing": "Some text here",
             "oddest_thing": "blehbleh",
             "user_email_address": "test@test.com",
             "action": "send"},
            follow=True)

        self.assertEquals(DataRequest.objects.all().count(), 2)

        data_request1 = DataRequest.objects.get(organization=self.organization)
        data_request2 = DataRequest.objects.get(organization=self.organization2)

        self.assertEquals(data_request1.organization, self.organization)
        self.assertEquals(data_request2.organization, self.organization2)

    def test_email_request_is_sent_correctly(self):
        response = self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"some_number": "1234567",
             "other_thing": "Some text here",
             "user_email_address": "test@test.com",
             "action": "send"},
            follow=True
            )

        # All requests were email requests
        self.assertContains(response, "All done!")

        self.assertContains(
            response, "Requests were sent to the following organizations")

        self.assertContains(response, "Organization")

        self.assertEquals(len(mail.outbox), 1)

        self.assertIn("Organization", mail.outbox[0].body)

    def test_mail_request_is_created_successfully(self):
        mail_organization = Organization.objects.create(
            name='Mail organization',
            address_line_one='Address one',
            address_line_two='Address two',
            postal_code='00000',
            country='Finland'
            )

        response = self.client.post(
            reverse("data_request:request_data", args=(mail_organization.id,)),
            {"some_number": "1234567",
             "action": "send"},
            follow=True
            )

        self.assertContains(response, "Further action required")
        self.assertContains(response, "Download PDF")

    def test_pending_email_request_displayed_correctly(self):
        email_organization = Organization.objects.create(
            name='Email organization',
            email_address='fake@address.com',
            address_line_one='Address one',
            address_line_two='Address two',
            postal_code='00000',
            country='Finland'
            )
        response = self.client.get(
            reverse("data_request:request_data",
                    args=(email_organization.id,)),
        )

        self.assertContains(
            response, "Following organizations will receive request by email")
        self.assertNotContains(
            response, "will have to be sent via mail"
        )

    def test_pending_mail_request_displayed_correctly(self):
        mail_organization = create_mail_organization(self)

        response = self.client.get(
            reverse("data_request:request_data", args=(mail_organization.id,)),
        )

        self.assertContains(
            response, "will have to be sent via mail"
        )
        self.assertNotContains(
            response, "Following organizations will receive request by email")

    def test_pending_email_request_needs_to_be_reviewed(self):
        email_organization = create_email_organization(self)

        response = self.client.get(
            reverse("data_request:request_data",
                    args=(email_organization.id,)))

        self.assertContains(response, "Review request")
        self.assertNotContains(response, "Create request")

    def test_pending_mail_request_doesnt_need_to_be_reviewed(self):
        mail_organization = create_mail_organization(self)

        response = self.client.get(
            reverse("data_request:request_data", args=(mail_organization.id,)))

        self.assertContains(response, "Create request")
        self.assertNotContains(response, "Review request")

    def test_pending_email_request_displays_email_body_for_request(self):
        email_organization = create_email_organization(self)

        response = self.client.post(
            reverse("data_request:request_data",
                    args=(email_organization.id,)),
            {"some_number": "1234567",
             "user_email_address": "test@test.com",
             "action": "review"})

        self.assertContains(
            response, "Please review the following email messages")
        self.assertContains(
            response, "Email organization</option>")

        self.assertContains(response, "Create request")
        self.assertNotContains(response, "Review request")


@isSeleniumTest()
class LiveDataRequestCreationTests(LiveServerTestCase):
    def test_selenium_email_request_can_be_created_successfully(self):
        self.organization = Organization.objects.create(
            name='Organization Two',
            email_address='fake@addressa.com',
            address_line_one='Address 2',
            address_line_two='Address 4',
            postal_code='012345',
            country='Sweden'
            )

        self.auth_field = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

        self.organization.authentication_fields.add(self.auth_field)

        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("data_request:request_data",
                              args=(self.organization.id,))))

        field = self.selenium.find_element_by_name("some_number")
        field.send_keys("12345678")

        field = self.selenium.find_element_by_name("user_email_address")
        field.send_keys("test@test.com")

        self.selenium.find_element_by_id("create_request").click()

        self.assertIn(
            "Please review the following email messages", self.selenium.page_source)

        self.selenium.find_element_by_id("create_request").click()

        self.assertIn("All done!", self.selenium.page_source)
        self.assertIn("Email requests sent!", self.selenium.page_source)

    def test_selenium_mail_request_can_be_created_successfully(self):
        self.organization = Organization.objects.create(
            name='Organization Two',
            address_line_one='Address 2',
            address_line_two='Address 4',
            postal_code='012345',
            country='Sweden'
            )

        self.auth_field = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

        self.organization.authentication_fields.add(self.auth_field)

        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("data_request:request_data",
                              args=(self.organization.id,))))

        field = self.selenium.find_element_by_name("some_number")
        field.send_keys("12345678")

        self.selenium.find_element_by_id("create_request").click()

        self.assertIn("Further action required", self.selenium.page_source)
        self.assertIn("Download PDF", self.selenium.page_source)


@isDjangoTest()
class AuthenticationAttributeValidationTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Organization',
            email_address='fake@address.com',
            address_line_one='Address one',
            address_line_two='Address two',
            postal_code='00000',
            country='Finland'
            )
        self.auth_field1 = AuthenticationField.objects.create(
            name="phone_number",
            title='Phone number',
            validator_regex="^[0-9]+$",
            help_text="This is a phone number")
        self.auth_field2 = AuthenticationField.objects.create(
            name='other_thing',
            title="Other thing")

        self.organization.authentication_fields.add(self.auth_field1)
        self.organization.authentication_fields.add(self.auth_field2)

    def test_authentication_field_with_regex_accepts_valid_input(self):
        response = self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"phone_number": "1234567",
             "other_thing": "Some text here",
             "user_email_address": "test@test.com"},
            follow=True
            )

        self.assertNotContains(response, "The value for this field was not valid")

    def test_authentication_field_with_regex_accepts_invalid_input(self):
        response = self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"phone_number": "notaphonenumber",
             "other_thing": "Some text here",
             "user_email_address": "test@test.com"},
            follow=True
            )

        self.assertContains(response, "The value for this field was not valid")

    def test_authentication_field_is_shown_with_help_text(self):
        response = self.client.get(
            reverse("data_request:request_data", args=(self.organization.id,)))

        self.assertContains(response, "This is a phone number")

        response = self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"phone_number": "notaphonenumber",
             "other_thing": "Some text here"},
            follow=True
            )

        self.assertNotContains(response, "This is a phone number")

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
                  reverse("data_request:faq")))

        self.assertIn("testtitle", self.selenium.page_source)
        self.assertIn("testcontent", self.selenium.page_source)
        self.assertIn("othertitle", self.selenium.page_source)
        self.assertIn("longer content with spaces", self.selenium.page_source)
        self.assertIn("somethingelse", self.selenium.page_source)
        self.assertIn("last, but not least", self.selenium.page_source)

    def test_selenium_faqs_order_can_be_prioritized(self):
        self.selenium.get("%s%s" % (self.live_server_url,
                reverse("data_request:faq")))

        accordion = self.selenium.find_element_by_id("accordion")
        faqs = accordion.find_elements_by_class_name("panel-title")
        self.assertIn("testtitle", faqs[0].text)
        self.assertIn("othertitle", faqs[2].text)
        self.assertIn("somethingelse", faqs[1].text)
