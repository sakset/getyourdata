from django.test import TestCase
from django.contrib.auth.models import Permission, User
from django.core.urlresolvers import reverse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from getyourdata.test import isDjangoTest, isSeleniumTest
from getyourdata.testcase import LiveServerTestCase

from organization.models import Organization, OrganizationDraft, Comment, AuthenticationField


def find_element_by_xpath(self, xpath, click_it=False, wait_time=10):
    """
    Finds element using XPATH
    """
    element = WebDriverWait(self.selenium, wait_time).until(
        EC.presence_of_element_located((
            By.XPATH, xpath))
    )
    if click_it:
        return element.click()
    else:
        return element


def create_simple_organization():
    """
    Creates simple organization with default information
    """
    return Organization.objects.create(
        name="Some organization",
        email_address="valid@address.com",
        verified=True)


def create_comment(user_organization, user_rating=1,
                   user_message="some message"):
    """
    Creates either default comment or custom comment
    """
    return Comment.objects.create(
        organization=user_organization,
        message=user_message,
        rating=user_rating
        )


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


def get_amount_of_organizations_on_page(self, page=-1):
    """
    Get organizations that are in organization list on current page
    """
    if page != -1:
        response = self.client.get(
            reverse("organization:list_organizations"),
            {"page": page})
    else:
        response = self.client.get(reverse("organization:list_organizations"))

    return response.content.count("Some organization")


@isDjangoTest()
class OrganizationListingTests(TestCase):
    def test_no_organizations_listed_when_no_organizations_exists(self):
        response = self.client.get(reverse("organization:list_organizations"))

        self.assertContains(response, "No organizations yet")

    def test_existing_organizations_listed_on_page(self):
        for i in range(0, 5):
            create_simple_organization()

        self.assertEquals(get_amount_of_organizations_on_page(self), 5)

    def test_only_15_organizations_are_listed_per_page(self):
        for i in range(0, 20):
            create_simple_organization()

        self.assertEquals(get_amount_of_organizations_on_page(self), 15)

    def test_correct_amount_of_organizations_listed_per_page(self):
        for i in range(0, 25):
            create_simple_organization()

        self.assertEquals(get_amount_of_organizations_on_page(self), 15)
        self.assertEquals(get_amount_of_organizations_on_page(self, 2), 10)


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

        self.assertContains(
            response,
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

        self.organization.authentication_fields.add(AuthenticationField.objects.get(id=self.auth_field1.id))

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
                "organization:edit_organization",
                args=(self.organization.id,)
            ),
            {"name": "Da Organization",
             "address_line_one": "Fake Street 44",
             "postal_code": "00234",
             "country": "Finland",
             "authentication_fields": [
                self.auth_field3.id, self.auth_field1.id],
             "g-recaptcha-response": "PASSED"}
        )

        self.assertRedirects(
            response,
            "/en/organizations/view/%s/" % self.organization.id,
            status_code=302)

        self.assertEquals(
            self.organization.authentication_fields.all().count(), 1)

        organization_draft = OrganizationDraft.objects.all()[0]

        self.assertEquals(
            organization_draft.authentication_fields.all().count(), 2)

    def test_user_can_create_organization_draft_with_email_address(self):
        response = self.client.post(
            reverse(
                "organization:edit_organization",
                args=(self.organization.id,)
            ),
            {"name": "Da Organization",
             "email_address": "some.email@random.com",
             "address_line_one": "",
             "postal_code": "",
             "country": "",
             "authentication_fields": [self.auth_field1.id],
             "g-recaptcha-response": "PASSED"}
        )

        self.assertRedirects(
            response,
            "/en/organizations/view/%s/" % self.organization.id,
            status_code=302)

        self.assertEquals(OrganizationDraft.objects.all().count(), 1)

    def test_user_cant_create_organization_without_authentication_fields(self):
        response = self.client.post(
            reverse(
                "organization:edit_organization",
                args=(self.organization.id,)
                ),
            {"name": "Da Organization",
             "address_line_one": "Fake Street 44",
             "postal_code": "00234",
             "country": "Finland",
             "authentication_fields": []}
        )

        self.assertContains(response,
                            "Authentication fields are required")

        self.assertEquals(OrganizationDraft.objects.all().count(), 0)

    def test_user_cant_create_organization_draft_without_valid_email_or_postal_address(self):
        response = self.client.post(
            reverse(
                "organization:edit_organization",
                args=(self.organization.id,)
                ),
            {"name": "Da Organization",
             "address_line_one": "",
             "postal_code": "00234",
             "country": "Finland",
             "authentication_fields": [self.auth_field1.id],
             "g-recaptcha-response": "PASSED"}
        )

        self.assertContains(
            response,
            "Organization profile must contain either a valid email "
            "address or postal information")

        self.assertEquals(OrganizationDraft.objects.all().count(), 0)

    def test_user_cant_create_organization_draft_without_any_changes(self):
        response = self.client.post(
            reverse(
                "organization:edit_organization",
                args=(self.organization.id,)
            ),
            {"name": "The Organization",
             "address_line_one": "Fake Street 4",
             "postal_code": "00234",
             "country": "Finland",
             "authentication_fields": [self.auth_field1.id],
             "g-recaptcha-response": "PASSED"}
        )

        self.assertContains(response, "Update form needs some changes for it to be sent!")

        self.assertEquals(OrganizationDraft.objects.all().count(), 0)


@isDjangoTest()
class OrganizationUpdateAdminTests(TestCase):
    def setUp(self):
        self.moderator_user = User.objects.create_user(
            'moderator', 'moderator@moderator.com', 'password')
        self.moderator_user.is_staff = True

        self.moderator_user.user_permissions.add(
            Permission.objects.get(codename='check_organization_draft'))
        self.moderator_user.user_permissions.add(
            Permission.objects.get(codename='change_organizationdraft'))
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
            if i < 26:
                char = unichr(97+i)
            else:
                char = 'z' + unichr(97+i-25)
            organization = Organization.objects.create(
                name='%s Organization' % char,
                email_address='fake@address.com',
                address_line_one='Address one',
                address_line_two='Address two',
                postal_code='00000',
                country='Finland',
                verified=True
                )

            organization.authentication_fields.add(self.auth_field1)

        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("organization:list_organizations")))

    def test_cant_create_request_with_no_selected_organizations(self):
        self.assertEquals(
            self.selenium.find_element_by_id("create-request").is_enabled(),
            False)
        self.assertIn("0 organizations selected", self.selenium.page_source)

    def test_select_single_organization_for_request(self):
        find_element_by_xpath(
            self,
            "(//input[@type='checkbox' and contains(@onclick, 'orgList')])[1]",
            click_it=True)

        self.assertIn("1 organization selected", self.selenium.page_source)

        find_element_by_xpath(
            self,
            "(//button[@id='create-request' and contains(@onclick, 'orgList')])",
            click_it=True)

        self.assertIn(
            "Fill in your details", self.selenium.page_source)

    def test_select_multiple_organizations_for_request(self):
        find_element_by_xpath(
            self,
            "(//input[@type='checkbox' and contains(@onclick, 'orgList')])[1]",
            click_it=True)
        find_element_by_xpath(
            self,
            "(//input[@type='checkbox' and contains(@onclick, 'orgList')])[2]",
            click_it=True)

        self.assertIn("2 organizations selected", self.selenium.page_source)

        find_element_by_xpath(
            self,
            "(//button[@id='create-request' and contains(@onclick, 'orgList')])",
            click_it=True)

        self.assertIn(
            "Fill in your details",
            self.selenium.page_source)

    def test_can_change_page_to_display_different_organizations(self):
        find_element_by_xpath(
            self,
            "(//a[@id='page-2' and contains(@onclick, 'orgList')])",
            click_it=True)

        find_element_by_xpath(
            self,
            "(//a[@id='page-2' and @onclick='' and text()='2'])")

        self.assertIn("p Organization", self.selenium.page_source)
        self.assertNotIn("a Organization", self.selenium.page_source)

        find_element_by_xpath(
            self,
            "(//a[@id='page-1' and contains(@onclick, 'orgList')])",
            click_it=True)

        find_element_by_xpath(
            self,
            "(//a[@id='page-1' and @onclick='' and text()='1'])")

        self.assertIn("a Organization", self.selenium.page_source)
        self.assertNotIn("p Organization", self.selenium.page_source)

    def test_user_can_select_multiple_organizations_from_different_pages(self):
        find_element_by_xpath(
            self,
            "(//input[@type='checkbox' and contains(@onclick, 'orgList')])[1]",
            click_it=True)
        find_element_by_xpath(
            self,
            "(//input[@type='checkbox' and contains(@onclick, 'orgList')])[2]",
            click_it=True)

        self.assertIn("2 organizations selected", self.selenium.page_source)

        find_element_by_xpath(
            self,
            "(//a[@id='page-2' and contains(@onclick, 'orgList')])",
            click_it=True)
        find_element_by_xpath(
            self,
            "(//a[@id='page-2' and @onclick='' and text()='2'])")

        find_element_by_xpath(
            self,
            "(//input[@type='checkbox' and contains(@onclick, 'orgList')])[1]",
            click_it=True)
        find_element_by_xpath(
            self,
            "(//input[@type='checkbox' and contains(@onclick, 'orgList')])[2]",
            click_it=True)

        self.assertIn("4 organizations selected", self.selenium.page_source)

        find_element_by_xpath(
            self,
            "(//a[@id='page-3' and contains(@onclick, 'orgList')])",
            click_it=True)
        find_element_by_xpath(
            self,
            "(//a[@id='page-3' and @onclick='' and text()='3'])")

        find_element_by_xpath(
            self,
            "(//input[@type='checkbox' and contains(@onclick, 'orgList')])[1]",
            click_it=True)
        find_element_by_xpath(
            self,
            "(//input[@type='checkbox' and contains(@onclick, 'orgList')])[2]",
            click_it=True)

        self.assertIn("6 organizations selected", self.selenium.page_source)


@isDjangoTest()
class CommentCreationTests(TestCase):

    def setUp(self):
        self.organization = create_simple_organization()

    def test_comment_can_be_created(self):
        create_comment(self.organization, 1, 'Test message')

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

        create_comment(self.organization, 1, 'Test message')
        create_comment(self.organization, 3, 'Test message2')

        self.assertEquals(self.organization.average_rating, '2.0')

        create_comment(self.organization, 1, 'Test message3')

        self.assertEquals(self.organization.average_rating, '1.7')


def pagination_can_be_seen(self):
    """
    Tries to find element that has class "pagination" if found returns True.
    """
    if self.selenium.find_elements_by_class_name("pagination"):
        return True
    else:
        return False


def is_pagination_shown_in_organization_list(self, number_of_organizations):
    """
    Check if pagination can be seen with certain amount of organizations in
    organizations list
    """
    for i in range(0, number_of_organizations):
        self.organization = create_simple_organization()

        self.organization.authentication_fields.add(self.auth_field1)

    self.selenium.get(
        "%s%s" % (self.live_server_url,
                  reverse("organization:list_organizations")))

    return pagination_can_be_seen(self)


@isSeleniumTest()
class OrganizationListPaginationShownTests(LiveServerTestCase):
    def setUp(self):
        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

    def test_pagination_isnt_shown_when_there_are_no_organization(self):
        self.assertFalse(is_pagination_shown_in_organization_list(self, 0))

    def test_pagination_isnt_shown_when_there_are_only_few_organization(self):
        self.assertFalse(is_pagination_shown_in_organization_list(self, 7))

    def test_pagination_is_shown_when_there_are_many_organization(self):
        self.assertTrue(is_pagination_shown_in_organization_list(self, 32))


def is_pagination_shown_in_view_organization(self, number_of_comments):
        """
        Check if pagination can be seen with certain amount of comments in
        organization view
        """
        for i in range(0, number_of_comments):
            create_comment(self.organization)

        self.selenium.get(
            "%s%s" % (self.live_server_url,
                      reverse("organization:view_organization",
                              args=(self.organization.id,))))

        return pagination_can_be_seen(self)


@isSeleniumTest()
class OrganizationViewPaginationShownTests(LiveServerTestCase):
    def setUp(self):
        self.organization = create_simple_organization()

        self.auth_field1 = AuthenticationField.objects.create(
            name="some_number",
            title='Some number')

        self.organization.authentication_fields.add(self.auth_field1)

    def test_pagination_isnt_shown_when_there_are_no_comments(self):
        self.assertFalse(is_pagination_shown_in_view_organization(self, 0))

    def test_pagination_isnt_shown_when_there_are_only_few_comments(self):
        self.assertFalse(is_pagination_shown_in_view_organization(self, 7))

    def test_pagination_is_shown_when_there_are_many_comments(self):
        self.assertTrue(is_pagination_shown_in_view_organization(self, 20))
