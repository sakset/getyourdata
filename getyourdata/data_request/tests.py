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
        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')
        self.auth_field2 = AuthenticationField.objects.create(
            name='other_thing',
            title="Other thing")

        self.assertEquals(len(self.organization.authentication_fields.all()), 0)

        self.organization.authentication_fields.add(self.auth_field1)
        self.organization.authentication_fields.add(self.auth_field2)

        self.assertEquals(len(self.organization.authentication_fields.all()), 2)
        self.assertEquals(DataRequest.objects.all().count(), 0)
        self.assertEquals(AuthenticationContent.objects.all().count(), 0)

        self.client.post(
            reverse("data_request:request_data", args=(self.organization.id,)),
            {"Some number": "1234567",
             "Other thing": "Some text here"},
            follow=True
            )

    def test_data_request_is_created(self):
        self.assertEquals(DataRequest.objects.all().count(), 1)

        data_request = DataRequest.objects.first()

        self.assertTrue(data_request.organization == self.organization)

    def test_authentication_contents_are_created(self):
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
