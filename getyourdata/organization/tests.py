from django.test import TestCase
from django.core.urlresolvers import reverse

from organization.models import Organization

class OrganizationCreationTests(TestCase):
    def test_organization_with_valid_email_address_can_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization",
             "email_address": "valid@address.com"},
            follow=True)

        self.assertContains(response, "Organization profile created")

        organization = Organization.objects.all()[0]

        self.assertEquals(organization.name, "The Organization")
        self.assertEquals(organization.email_address, "valid@address.com")

    def test_organization_with_invalid_email_address_cant_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization",
             "email_address": "notavalidaddrss"},
            follow=True)

        self.assertNotContains(response, "Organization profile created")

        self.assertEquals(Organization.objects.all().count(), 0)

    def test_organization_with_missing_contact_information_cant_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization"},
            follow=True)

        self.assertContains(
            response, "Organization profile must contain either")
        self.assertEquals(Organization.objects.all().count(), 0)

    def test_organization_with_postal_information_can_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization",
             "address_line_one": "Fake Street 4",
             "postal_code": "00444",
             "country": "Finland"},
            follow=True)

        self.assertContains(response, "Organization profile created")

        organization = Organization.objects.all()[0]

        self.assertEquals(organization.name, "The Organization")
        self.assertEquals(organization.address_line_one, "Fake Street 4")
        self.assertEquals(organization.postal_code, "00444")
        self.assertEquals(organization.country, "Finland")

    def test_organization_with_missing_postal_information_cant_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization",
             "address_line_one": "Fake Street 4"},
            follow=True)

        self.assertNotContains(response, "Organization profile created")
        self.assertEquals(Organization.objects.all().count(), 0)

    def test_organization_with_valid_postal_and_email_can_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization",
             "address_line_one": "Fake Street 4",
             "postal_code": "00444",
             "country": "Finland",
             "email_address": "fake@address.com"},
            follow=True)

        self.assertContains(response, "Organization profile created")

        organization = Organization.objects.all()[0]

        self.assertEquals(organization.name, "The Organization")
        self.assertEquals(organization.address_line_one, "Fake Street 4")
        self.assertEquals(organization.postal_code, "00444")
        self.assertEquals(organization.country, "Finland")
        self.assertEquals(organization.email_address, "fake@address.com")

def create_organization(test_case):
    response = test_case.client.post(
        reverse("organization:new_organization"),
        {"name": "The Organization",
         "email_address": "valid@address.com"},
        follow=True)

    test_case.assertContains(response, "Organization profile created")

class OrganizationListingTests(TestCase):
    def test_no_organizations_listed_when_no_organizations_exists(self):
        response = self.client.get(reverse("organization:list_organizations"))

        self.assertContains(response, "No organizations yet")

    def test_existing_organizations_listed_on_page(self):
        for i in range(0, 5):
            create_organization(self)

        response = self.client.get(reverse("organization:list_organizations"))

        self.assertContains(response, "The Organization", 5)

    def test_only_15_organizations_are_listed_per_page(self):
        for i in range(0, 20):
            create_organization(self)

        response = self.client.get(reverse("organization:list_organizations"))

        self.assertContains(response, "The Organization", 15)

    def test_correct_amount_of_organizations_listed_per_page(self):
        for i in range(0, 25):
            create_organization(self)

        response = self.client.get(reverse("organization:list_organizations"))

        self.assertContains(response, "The Organization", 15)

        response = self.client.get(
            reverse("organization:list_organizations"),
            {"page": 2})

        self.assertContains(response, "The Organization", 10)
