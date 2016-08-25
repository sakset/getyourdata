from django.core.urlresolvers import reverse
from django.core import mail
from django.test import TestCase

from getyourdata.test import isDjangoTest, isSeleniumTest
from getyourdata.testcase import LiveServerTestCase

from data_request.models import DataRequest, AuthenticationContent
from organization.models import Organization, AuthenticationField


def create_email_organization(test_case):
    """
    Creates organization that accepts emails
    """
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
    """
    Creates organization that accepts mail
    """
    mail_organization = Organization.objects.create(
        name='Mail organization',
        address_line_one='Address one',
        address_line_two='Address two',
        postal_code='00000',
        country='Finland'
    )

    mail_organization.authentication_fields.add(test_case.auth_field1)

    return mail_organization


def create_dummy_organization(new_name='Organization Two', new_email_address='fake@addressa.com',
                              new_address_line_one='Address 2', new_address_line_two='Address 4',
                              new_postal_code='012345', new_country='Sweden'):
    """
    Creates dummy organization either with default or custom values.
    """
    return Organization.objects.create(
        name=new_name,
        email_address=new_email_address,
        address_line_one=new_address_line_one,
        address_line_two=new_address_line_two,
        postal_code=new_postal_code,
        country=new_country
    )


@isDjangoTest()
class DataRequestCreationTests(TestCase):
    def setUp(self):
        self.organization = create_dummy_organization('Organization', 'fake@address.com',
                                                      'Address one', 'Address two',
                                                      '00000', 'Finland')
        self.organization2 = create_dummy_organization()
        self.organization3 = create_dummy_organization('Organization Three', 'fake@addressb.com',
                                                       'Address 5', 'Address 6',
                                                       '123456', 'Estonia')

        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number',
            help_text='some text')
        self.auth_field2 = AuthenticationField.objects.create(
            name='other_thing',
            title="Other thing",
            help_text='other text')
        self.auth_field3 = AuthenticationField.objects.create(
            name='oddest_thing',
            title="Oddest thing",
            help_text='oddest text')

        self.assertEquals(self.organization.authentication_fields.all().count(), 0)

        self.organization.authentication_fields.add(self.auth_field1)
        self.organization.authentication_fields.add(self.auth_field2)

        self.organization2.authentication_fields.add(self.auth_field2)
        self.organization2.authentication_fields.add(self.auth_field3)

        self.organization3.authentication_fields.add(self.auth_field1)
        self.organization3.authentication_fields.add(self.auth_field2)
        self.organization3.authentication_fields.add(self.auth_field3)

        self.assertEquals(self.organization.authentication_fields.all().count(), 2)
        self.assertEquals(self.organization2.authentication_fields.all().count(), 2)
        self.assertEquals(DataRequest.objects.all().count(), 0)
        self.assertEquals(AuthenticationContent.objects.all().count(), 0)

    def test_data_request_form_is_correct(self):
        response = self.client.get(reverse("data_request:request_data",
                                           args=(self.organization.id,)))

        self.assertContains(response, "Some number")
        self.assertContains(response, "Other thing")
        self.assertContains(response, "Fill in your details")

    def test_required_by_is_present_when_supposed(self):
        response = self.client.get(reverse("data_request:request_data",
            args = ("%d,%d,%d" % (self.organization.id, self.organization2.id, self.organization3.id),)))

        self.assertContains(response, "Required by:")


    def test_required_by_is_not_present_when_supposed(self):
        response = self.client.get(reverse("data_request:request_data",
        args = (self.organization.id,)))

        self.assertNotContains(response, "Required by:")

    def test_data_request_form_with_multiple_organizations_is_correct(self):
        response = self.client.get(
            reverse("data_request:request_data",
                    args=("%d,%d" % (self.organization.id,
                                     self.organization2.id),)))

        self.assertContains(response, "Some number")
        self.assertContains(response, "Other thing")
        self.assertContains(response, "Oddest thing")

    def test_data_request_is_created(self):
        self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"some_number": "1234567",
             "other_thing": "Some text here",
             "user_email_address": "test@test.com",
             "send": "true",
             "g-recaptcha-response": "PASSED"},
            follow=True
        )

        self.assertEquals(DataRequest.objects.all().count(), 1)

        data_request = DataRequest.objects.first()

        self.assertTrue(data_request.organization == self.organization)
        self.assertTrue(data_request.user_email_address == "test@test.com")

    def test_multiple_data_requests_can_be_created(self):
        self.client.post(
            reverse("data_request:request_data",
                    args=("%d,%d" % (self.organization.id,
                                     self.organization2.id),)),
            {"some_number": "1234567",
             "other_thing": "Some text here",
             "oddest_thing": "blehbleh",
             "user_email_address": "test@test.com",
             "send": "true",
             "g-recaptcha-response": "PASSED"},
            follow=True)

        self.assertEquals(DataRequest.objects.all().count(), 2)

        data_request1 = DataRequest.objects.get(organization=self.organization)
        data_request2 = DataRequest.objects.get(organization=self.organization2)

        self.assertEquals(data_request1.organization, self.organization)
        self.assertEquals(data_request2.organization, self.organization2)
        self.assertEquals(data_request1.user_email_address, "test@test.com")
        self.assertEquals(data_request2.user_email_address, "test@test.com")

    def test_email_request_is_sent_correctly(self):
        response = self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"some_number": "1234567",
             "other_thing": "Some text here",
             "user_email_address": "test@test.com",
             "send": "true",
             "g-recaptcha-response": "PASSED"},
            follow=True
        )

        # All requests were email requests
        self.assertContains(response, "You have successfully finished")

        self.assertContains(response, "Organization")

        # User gets a copy of his request + a feedback message
        self.assertEquals(len(mail.outbox), 2)

        self.assertIn("Organization", mail.outbox[0].body)

    def test_mail_request_is_created_successfully(self):
        mail_organization = create_mail_organization(self)

        response = self.client.post(
            reverse("data_request:request_data", args=(mail_organization.id,)),
            {"some_number": "1234567",
             "send": "true",
             "g-recaptcha-response": "PASSED"},
            follow=True
        )

        self.assertContains(response, "Further action required")
        self.assertContains(response, "Download PDF")
        self.assertNotContains(response, "A copy of the PDF")

    def test_mail_request_copy_can_be_sent_successfully(self):
        mail_organization = create_mail_organization(self)

        response = self.client.post(
            reverse("data_request:request_data", args=(mail_organization.id,)),
            {"some_number": "1234567",
             "user_email_address": "test@test.com",
             "send_mail_request_copy": True,
             "send": "true",
             "g-recaptcha-response": "PASSED"},
            follow=True
        )

        self.assertContains(response, "A copy of the PDF")

        # User receives a copy of the PDF and a feedback message in one message
        self.assertEquals(len(mail.outbox), 1)

    def test_mail_request_copy_can_be_sent_successfully_with_email_requests(self):
        mail_organization = create_mail_organization(self)
        email_organization = create_email_organization(self)

        response = self.client.post(
            reverse("data_request:request_data", args=(
                "%s,%s" % (mail_organization.id, email_organization.id),)),
            {"some_number": "1234567",
             "user_email_address": "test@test.com",
             "send_mail_request_copy": True,
             "send": "true",
             "g-recaptcha-response": "PASSED"},
            follow=True
        )

        self.assertContains(response, "A copy of the PDF")

    def test_pending_email_request_displayed_correctly(self):
        email_organization = create_email_organization(self)
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

    def test_pending_email_request_displays_email_body_for_request(self):
        email_organization = create_email_organization(self)

        response = self.client.post(
            reverse("data_request:request_data",
                    args=(email_organization.id,)),
            {"some_number": "1234567",
             "user_email_address": "test@test.com",
             "review": "true"})

        self.assertContains(
            response, "Please review the following message")
        self.assertContains(
            response, "Email organization")

        self.assertContains(response, "Send request")
        self.assertNotContains(response, "Review request")

    def test_feedback_is_displayed_correctly(self):
        email_organization = create_email_organization(self)
        mail_organization = create_mail_organization(self)

        response = self.client.get(
            reverse("data_request:give_feedback", args=(
                "%s,%s" % (mail_organization.id, email_organization.id),)))

        self.assertContains(response, email_organization.name)
        self.assertContains(response, mail_organization.name)


@isSeleniumTest()
class LiveDataRequestCreationTests(LiveServerTestCase):
    def test_selenium_email_request_can_be_created_successfully(self):
        self.organization = create_dummy_organization()

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
            "Please review the following message", self.selenium.page_source)

        self.selenium.find_element_by_id("create_request").click()

        self.assertIn("You have successfully finished", self.selenium.page_source)
        self.assertIn("You should receive a copy of your email requests", self.selenium.page_source)

    def test_selenium_mail_request_can_be_created_successfully(self):
        self.organization = create_dummy_organization(new_email_address="")

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

        self.assertIn(
            "Please review the following message", self.selenium.page_source)

        self.selenium.find_element_by_id("create_request").click()

        self.assertIn("Further action required", self.selenium.page_source)
        self.assertIn("Download PDF", self.selenium.page_source)


def is_phone_number_valid(self, number):
    """
    Check if phone number posted in request data is valid
    """
    response = self.client.post(
        reverse("data_request:request_data", args=(self.organization.id,)),
        {"phone_number": number,
         "other_thing": "Some text here",
         "user_email_address": "test@test.com"},
        follow=True
    )
    return response.content.count("The value for this field was not valid")


@isDjangoTest()
class AuthenticationAttributeValidationTests(TestCase):
    def setUp(self):
        self.organization = create_dummy_organization('Organization', 'fake@address.com',
                                                      'Address one', 'Address two',
                                                      '00000', 'Finland')
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
        self.assertEquals(is_phone_number_valid(self, "1234567"), 0)

    def test_authentication_field_with_regex_accepts_invalid_input(self):
        self.assertEquals(is_phone_number_valid(self, "notaphonenumber"), 1)

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

        self.assertContains(response, "This is a phone number")
        self.assertContains(response, "The value for this field was not valid")


@isSeleniumTest()
class ProcessBarNavigationTests(LiveServerTestCase):
    def setUp(self):
        self.organization = create_dummy_organization()

        self.auth_field = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

        self.organization.authentication_fields.add(self.auth_field)

        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("data_request:request_data",
                              args=(self.organization.id,))))

    def test_selenium_back_to_organization_list_works(self):
        self.selenium.find_element_by_id("back-to-organization-list").click()

        self.assertIn("Add organization", self.selenium.page_source)

    def test_selenium_back_to_authentication_fields_input_works(self):
        field = self.selenium.find_element_by_name("some_number")
        field.send_keys("12345678")

        field = self.selenium.find_element_by_name("user_email_address")
        field.send_keys("test@test.com")

        self.selenium.find_element_by_id("create_request").click()

        # now we go back to previous step, the input values should still be there.

        self.selenium.find_element_by_id("back-to-input-details").click()

        self.assertIn("12345678", self.selenium.page_source)
        self.assertIn("test@test.com", self.selenium.page_source)

    def test_selenium_back_to_previous_steps_when_all_done_not_allowed(self):
        field = self.selenium.find_element_by_name("some_number")
        field.send_keys("12345678")

        field = self.selenium.find_element_by_name("user_email_address")
        field.send_keys("test@test.com")

        self.selenium.find_element_by_id("create_request").click()

        # here we are at the review message step. let's move on.

        self.selenium.find_element_by_id("create_request").click()

        # if we are, we make sure that the process bar navigation buttons are no longer functional
        # in other words the elements with respective id's are not found.

        element_lookup = self.selenium.find_elements_by_id("back-to-organization-list")
        self.assertFalse(len(element_lookup) > 0)

        element_lookup = self.selenium.find_elements_by_id("back-to-input-details")
        self.assertFalse(len(element_lookup) > 0)


def is_organization_feedback_valid(self, second_message, expected_response):
    response = self.client.post(
        reverse("data_request:submit_feedback"),
        {"org_ids": self.org_ids,
         "rating_" + self.org_id_one: 1,
         "message_" + self.org_id_one: "First Organization gets one",
         "rating_" + self.org_id_two: 2,
         "message_" + self.org_id_two: second_message,
         "rating_" + self.org_id_three: 3,
         "message_" + self.org_id_three: "Third Org is the hi-scorer with three",
         "g-recaptcha-response": "PASSED"},
        follow=True)
    self.assertContains(response, expected_response)


@isDjangoTest()
class OrganizationRatingTests(TestCase):
    def setUp(self):
        self.organization_one = create_dummy_organization('FirstOrganization')
        self.organization_two = create_dummy_organization('SecondOrganization')
        self.organization_three = create_dummy_organization('ThirdOrganization')

        self.auth_field = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

        self.organization_one.authentication_fields.add(self.auth_field)
        self.organization_two.authentication_fields.add(self.auth_field)
        self.organization_three.authentication_fields.add(self.auth_field)

        self.organizations = [
            self.organization_one,
            self.organization_two,
            self.organization_three
        ]

        # a few help-variables to make code inside the methods more readable
        org_ids = [str(organization.id) for organization in self.organizations]
        self.org_ids = ",".join(org_ids)
        self.org_id_one = str(self.organization_one.id)
        self.org_id_two = str(self.organization_two.id)
        self.org_id_three = str(self.organization_three.id)

    def test_user_can_rate_organizations(self):
        is_organization_feedback_valid(self, "Second Organization has to live with two",
                                             "Thank you for your contribution!")

    def test_no_missing_message_allowed(self):
        response = self.client.post(
            reverse("data_request:submit_feedback"),
            {"org_ids": self.org_ids,
             "rating_" + self.org_id_one: 1,
             "message_" + self.org_id_one: "First Organization gets one",
             "rating_" + self.org_id_two: 2,
             "message_" + self.org_id_two: "Second Organization has to live with two",
             "rating_" + self.org_id_three: 3,
             "g-recaptcha-response": "PASSED"},
            follow=True)
        self.assertContains(response, "Some of the fields were invalid or missing")

    def test_no_empty_message_allowed(self):
        is_organization_feedback_valid(self, "", "Some of the fields were invalid or missing")
