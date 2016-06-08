from django.core.urlresolvers import reverse
from django.test import TestCase

from data_request.models import DataRequest, AuthenticationContent
from organization.models import Organization, AuthenticationField


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

    def test_data_request_is_created(self):
        self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"some_number": "1234567",
             "other_thing": "Some text here"},
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
             "oddest_thing": "blehbleh"},
            follow=True)

        self.assertEquals(DataRequest.objects.all().count(), 2)

        data_request1 = DataRequest.objects.get(organization=self.organization)
        data_request2 = DataRequest.objects.get(organization=self.organization2)

        self.assertEquals(data_request1.organization, self.organization)
        self.assertEquals(data_request2.organization, self.organization2)

    def test_authentication_contents_are_created(self):
        self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"some_number": "1234567",
             "other_thing": "Some text here"},
            follow=True
            )

        data_request = DataRequest.objects.first()

        self.assertTrue(data_request.organization == self.organization)

        auth_contents = data_request.auth_contents.all()

        self.assertEquals(auth_contents.count(), 2)

        first_content = AuthenticationContent.objects.get(
            auth_field=self.auth_field1,
            data_request=data_request
            )
        self.assertEquals(first_content.content, '1234567')

        second_content = AuthenticationContent.objects.get(
            auth_field=self.auth_field2,
            data_request=data_request
            )
        self.assertEquals(second_content.content, 'Some text here')

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
             "other_thing": "Some text here"},
            follow=True
            )

        self.assertNotContains(response, "The value for this field was not valid")

    def test_authentication_field_with_regex_accepts_invalid_input(self):
        response = self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"phone_number": "notaphonenumber",
             "other_thing": "Some text here"},
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
