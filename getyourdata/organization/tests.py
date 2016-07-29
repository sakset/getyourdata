from django.test import TestCase
from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from getyourdata.test import isDjangoTest, isSeleniumTest
from getyourdata.testcase import LiveServerTestCase

from organization.models import Organization, OrganizationDraft, Comment, AuthenticationField


@isDjangoTest()
class OrganizationCreationTests(TestCase):
    def setUp(self):
        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

    def test_organization_with_valid_email_address_can_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization",
             "email_address": "valid@address.com",
             "authentication_fields": (self.auth_field1.id,),
             "g-recaptcha-response": "PASSED"},
            follow=True)

        self.assertContains(response, "Organization profile created")

        organization = Organization.objects.all()[0]

        self.assertEquals(organization.name, "The Organization")
        self.assertEquals(organization.email_address, "valid@address.com")

    def test_organization_with_invalid_email_address_cant_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization",
             "email_address": "notavalidaddrss",
             "authentication_fields": (self.auth_field1.id,)},
            follow=True)

        self.assertNotContains(response, "Organization profile created")

        self.assertEquals(Organization.objects.all().count(), 0)

    def test_organization_with_missing_contact_information_cant_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization",
             "authentication_fields": (self.auth_field1.id,)},
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
             "country": "Finland",
             "authentication_fields": (self.auth_field1.id,),
             "g-recaptcha-response": "PASSED"},
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
             "address_line_one": "Fake Street 4",
             "authentication_fields": (self.auth_field1.id,)},
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
             "email_address": "fake@address.com",
             "authentication_fields": (self.auth_field1.id,),
             "g-recaptcha-response": "PASSED"},
            follow=True)

        self.assertContains(response, "Organization profile created")

        organization = Organization.objects.all()[0]

        self.assertEquals(organization.name, "The Organization")
        self.assertEquals(organization.address_line_one, "Fake Street 4")
        self.assertEquals(organization.postal_code, "00444")
        self.assertEquals(organization.country, "Finland")
        self.assertEquals(organization.email_address, "fake@address.com")

    def test_organization_with_no_authentication_fields_cant_be_added(self):
        response = self.client.post(
            reverse("organization:new_organization"),
            {"name": "The Organization",
             "address_line_one": "Fake Street 4",
             "postal_code": "00444",
             "country": "Finland",
             "email_address": "fake@address.com"},
            follow=True)

        self.assertNotContains(response, "Organization profile created")

        self.assertEquals(Organization.objects.all().count(), 0)


def create_organization(test_case):
    Organization.objects.create(
        name="The Organization",
        email_address="valid@address.com",
        verified=True)


def verify_all_organizations():
    Organization.objects.all().update(verified=True)


@isDjangoTest()
class OrganizationListingTests(TestCase):
    def test_no_organizations_listed_when_no_organizations_exists(self):
        response = self.client.get(reverse("organization:list_organizations"))

        self.assertContains(response, "No organizations yet")

    def test_existing_organizations_listed_on_page(self):
        for i in range(0, 5):
            create_organization(self)
        verify_all_organizations()

        response = self.client.get(reverse("organization:list_organizations"))

        self.assertContains(response, "The Organization", 5)

    def test_only_15_organizations_are_listed_per_page(self):
        for i in range(0, 20):
            create_organization(self)
        verify_all_organizations()

        response = self.client.get(reverse("organization:list_organizations"))

        self.assertContains(response, "The Organization", 15)

    def test_correct_amount_of_organizations_listed_per_page(self):
        for i in range(0, 25):
            create_organization(self)
        verify_all_organizations()

        response = self.client.get(reverse("organization:list_organizations"))

        self.assertContains(response, "The Organization", 15)

        response = self.client.get(
            reverse("organization:list_organizations"),
            {"page": 2})

        self.assertContains(response, "The Organization", 10)



@isDjangoTest()
class OrganizationViewTests(TestCase):
    def test_organization_postal_contact_details_displayed_if_available(self):
        organization = Organization.objects.create(
            name="The Organization",
            address_line_one="Fake Street 4",
            postal_code="00234",
            country="Finland",
            verified=True)

        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

        response = self.client.get(
            reverse("organization:view_organization", args=(organization.id,)))

        self.assertContains(response, "Fake Street 4")
        self.assertContains(response, "00234")
        self.assertContains(response, "Finland")

    def test_organization_email_contact_details_displayed_if_available(self):
        organization = Organization.objects.create(
            name="The Organization",
            email_address="example@example.com",
            verified=True)

        response = self.client.get(
            reverse("organization:view_organization", args=(organization.id,)))

        self.assertContains(response, "example@example.com")

    def test_organization_page_has_warning_if_unverified(self):
        organization = Organization.objects.create(
            name="The Organization",
            email_address="example@example.com",
            verified=False)

        response = self.client.get(
            reverse("organization:view_organization", args=(organization.id,)))

        self.assertContains(response,
            "The contact details for this organization have not been verified")


@isDjangoTest()
class OrganizationUpdateTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="The Organization",
            address_line_one="Fake Street 4",
            postal_code="00234",
            country="Finland",
            verified=True)

        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

        self.auth_field2 = AuthenticationField.objects.create(
            name="some_value",
            title='Some Value')

        self.auth_field3 = AuthenticationField.objects.create(
            name="some_string",
            title='Some string')

    def test_user_can_create_organization_draft(self):
        response = self.client.get(
            reverse(
                "organization:edit_organization",
                args=(self.organization.id,)))

        self.assertContains(response, "Fake Street 4")
        self.assertContains(response, "00234")
        self.assertContains(response, "Finland")

        response = self.client.post(
            reverse(
                "organization:edit_organization", args=(self.organization.id,)),
                {"name": "Da Organization",
                 "address_line_one": "Fake Street 44",
                 "postal_code": "00234",
                 "country": "Finland",
                 "authentication_fields": [
                    self.auth_field3.id, self.auth_field1.id],
                 "g-recaptcha-response": "PASSED"})

        self.assertContains(response, "Updated organization profile sent")

        self.assertEquals(
            self.organization.authentication_fields.all().count(), 0)

        organization_draft = OrganizationDraft.objects.all()[0]

        self.assertEquals(
            organization_draft.authentication_fields.all().count(), 2)

    def test_user_cant_create_organization_without_authentication_fields(self):
        response = self.client.post(
            reverse(
                "organization:edit_organization", args=(self.organization.id,)),
                {"name": "Da Organization",
                 "address_line_one": "Fake Street 44",
                 "postal_code": "00234",
                 "country": "Finland",
                 "authentication_fields": []})

        self.assertNotContains(response, "Updated organization profile sent")

        self.assertEquals(OrganizationDraft.objects.all().count(), 0)


@isDjangoTest()
class OrganizationUpdateAdminTests(TestCase):
    def setUp(self):
        self.moderator_user = User.objects.create_user(
            'moderator', 'moderator@moderator.com', 'password')
        self.moderator_user.is_staff = True

        self.moderator_user.user_permissions.add(Permission.objects.get(
            codename='check_organization_draft'))
        self.moderator_user.user_permissions.add(Permission.objects.get(
            codename='change_organizationdraft'))
        self.moderator_user.save()
        self.client.login(username="moderator", password="password")

        self.organization = Organization.objects.create(
            name="The Organization",
            address_line_one="Fake Street 4",
            postal_code="00234",
            country="Finland",
            verified=True)

        self.organization_draft = OrganizationDraft.objects.create(
            original_organization=self.organization,
            name="Da Organization",
            address_line_one="Fake Street 44",
            postal_code="00234",
            country="Finland")

        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

        self.auth_field2 = AuthenticationField.objects.create(
            name="some_value",
            title='Some Value')

        self.organization_draft.authentication_fields.add(self.auth_field2)

    def test_guest_cant_review_organization_draft(self):
        self.client.logout()

        response = self.client.get(
            reverse(
                "admin:organization_organizationdraft_check_organization_draft",
                args=(self.organization_draft.id,)))

        self.assertContains(
            response, "You don't have the permission to do this.",
            status_code=422)

    def test_moderator_can_review_organization_draft(self):
        response = self.client.get(
            reverse(
                "admin:organization_organizationdraft_check_organization_draft",
                args=(self.organization_draft.id,)))

        self.assertContains(response, "Organization draft")

        self.assertContains(response, "The Organization")
        self.assertContains(response, "Da Organization")

        self.assertContains(response, "Fake Street 4")
        self.assertContains(response, "Fake Street 44")

        self.assertContains(response, "Some Value")

    def test_moderator_can_review_organization_draft_and_update_details(self):
        response = self.client.post(
            reverse(
                "admin:organization_organizationdraft_check_organization_draft",
                args=(self.organization_draft.id,)),
            {"update": True},
            follow=True)

        self.assertContains(
            response,
            "The organization Da Organization was updated with new details")

        self.assertContains(response, "Review again")
        self.assertContains(response, "Updated")

        organization = Organization.objects.all()[0]

        self.assertEquals(organization.name, "Da Organization")
        self.assertEquals(organization.address_line_one, "Fake Street 44")
        self.assertEquals(organization.verified, True)

        organization_draft = OrganizationDraft.objects.all()[0]

        self.assertEquals(organization_draft.checked, True)
        self.assertEquals(organization_draft.updated, True)

    def test_moderator_can_review_and_ignore_organization_draft(self):
        response = self.client.post(
            reverse(
                "admin:organization_organizationdraft_check_organization_draft",
                args=(self.organization_draft.id,)),
            {"ignore": True},
            follow=True)

        self.assertContains(
            response,
            "The organization draft for The Organization was ignored")

        self.assertContains(response, "Review again")
        self.assertContains(response, "Ignored")

        organization = Organization.objects.all()[0]

        self.assertEquals(organization.name, "The Organization")
        self.assertEquals(organization.address_line_one, "Fake Street 4")

        organization_draft = OrganizationDraft.objects.all()[0]

        self.assertEquals(organization_draft.checked, True)
        self.assertEquals(organization_draft.ignored, True)


@isSeleniumTest()
class OrganizationListJavascriptTests(LiveServerTestCase):
    def setUp(self):
        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

        # Create three pages worth of organizations
        for i in range(0, 45):
            organization = Organization.objects.create(
                name='Organization %d' % i,
                email_address='fake@address.com',
                address_line_one='Address one',
                address_line_two='Address two',
                postal_code='00000',
                country='Finland',
                verified=True
                )

            organization.authentication_fields.add(self.auth_field1)

    def test_cant_create_request_with_no_selected_organizations(self):
        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("organization:list_organizations")))

        self.assertEquals(
            self.selenium.find_element_by_id("create-request").is_enabled(),
            False)

        self.assertIn("0 organizations selected", self.selenium.page_source)

    def test_select_single_organization_for_request(self):
        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("organization:list_organizations")))

        self.selenium.find_element(
            By.XPATH, "(//input[@type='checkbox'])[1]").click()
        self.assertIn("1 organization selected", self.selenium.page_source)

        self.selenium.find_element_by_id("create-request").click()

        self.assertIn(
            "Request your data from Organization 0", self.selenium.page_source)

    def test_select_multiple_organizations_for_request(self):
        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("organization:list_organizations")))

        self.selenium.find_element(
            By.XPATH, "(//input[@type='checkbox'])[1]").click()
        self.selenium.find_element(
            By.XPATH, "(//input[@type='checkbox'])[2]").click()
        self.assertIn("2 organizations selected", self.selenium.page_source)

        self.selenium.find_element_by_id("create-request").click()

        self.assertIn(
            "Request your data from multiple organizations",
            self.selenium.page_source)

    def test_can_change_page_to_display_different_organizations(self):
        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("organization:list_organizations")))

        element = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, "page-2"))
        )
        element.click()

        self.assertIn("Organization 15", self.selenium.page_source)
        self.assertNotIn("Organization 0", self.selenium.page_source)

        element = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, "page-1"))
        )
        element.click()

        self.assertIn("Organization 0", self.selenium.page_source)
        self.assertNotIn("Organization 15", self.selenium.page_source)

    def test_user_can_select_multiple_organizations_from_different_pages(self):
        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("organization:list_organizations")))

        self.selenium.find_element(
            By.XPATH, "(//input[@type='checkbox'])[1]").click()
        self.selenium.find_element(
            By.XPATH, "(//input[@type='checkbox'])[2]").click()
        self.assertIn("2 organizations selected", self.selenium.page_source)

        self.selenium.find_element_by_id("page-2").click()

        self.selenium.find_element(
            By.XPATH, "(//input[@type='checkbox'])[1]").click()
        self.selenium.find_element(
            By.XPATH, "(//input[@type='checkbox'])[2]").click()
        self.assertIn("4 organizations selected", self.selenium.page_source)

        self.selenium.find_element_by_id("page-3").click()

        self.selenium.find_element(
            By.XPATH, "(//input[@type='checkbox'])[1]").click()
        self.selenium.find_element(
            By.XPATH, "(//input[@type='checkbox'])[2]").click()
        self.assertIn("6 organizations selected", self.selenium.page_source)

    def test_selenium_icon_displayed_next_to_organization_that_accepts_email(self):
        Organization.objects.all().update(email_address="")
        organization = Organization.objects.all()[0]
        organization.email_address = "fake@address.com"
        organization.save()

        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("organization:list_organizations")))

        try:
            element = self.selenium.find_element(By.XPATH, "(//span[@class='glyphicon glyphicon-cloud'])")
            self.assertTrue(element)
        except NoSuchElementException:
            self.fail("'Accepts email requests' element not found")

    def test_selenium_icon_displayed_next_to_organization_that_accepts_mail(self):
        Organization.objects.all().update(
            address_line_one="",
            postal_code="",
            country="")
        organization = Organization.objects.all()[0]
        organization.address_line_one = "Fake Street"
        organization.postal_code = "012345"
        organization.country = "Finland"
        organization.verified = True
        organization.save()

        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("organization:list_organizations")))

        try:
            element = self.selenium.find_element(By.XPATH, "(//span[@class='glyphicon glyphicon-envelope'])")
            self.assertTrue(element)
        except NoSuchElementException:
            self.fail("'Accepts postal requests' element not found")


@isDjangoTest()
class CommentCreationTests(TestCase):

    def setUp(self):
        self.organization = Organization.objects.create(
            name="The Organization",
            address_line_one="Fake Street 4",
            postal_code="00234",
            country="Finland",
            verified=True)

    def test_comment_can_be_created(self):
        Comment.objects.create(
            organization=self.organization,
            message='Test message',
            rating=1
        )
        self.assertEquals(self.organization.comments.all().count(), 1)

    def test_user_can_create_a_comment(self):
        response = self.client.post(
            reverse("organization:view_organization",
                    args=(self.organization.id,)),
            {"message": "It is okay.",
             "rating": 3,
             "g-recaptcha-response": "PASSED"},
            follow=True)

        self.assertContains(response, "It is okay.")
        self.assertContains(response, "Thank you for your feedback!")

    def test_organization_rating_average(self):
        self.assertEquals(self.organization.average_rating, '0')

        Comment.objects.create(
            organization=self.organization,
            message='Test message',
            rating=1
        )

        Comment.objects.create(
            organization=self.organization,
            message='Test message2',
            rating=3
        )

        self.assertEquals(self.organization.average_rating, '2.0')

        Comment.objects.create(
            organization=self.organization,
            message='Test message3',
            rating=1
        )

        self.assertEquals(self.organization.average_rating, '1.7')
