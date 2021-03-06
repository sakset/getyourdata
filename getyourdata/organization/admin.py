from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from modeltranslation.admin import TranslationAdmin

from organization.models import (Organization, AuthenticationField,
                                 Register, OrganizationDraft, Comment)
from organization import admin_views


@admin.register(AuthenticationField)
class AuthenticationFieldAdmin(TranslationAdmin):
    list_display = [
        'name',
        'created_on',
        'order',
    ]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'verified',
        'requested_amount',
        'created_on',
        'updated_on',
    ]


@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_on',
    ]


@admin.register(OrganizationDraft)
class OrganizationDraftAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'original_organization',
        'check_organization_draft',
        'created_on',
        'updated_on',
    ]

    def get_urls(self):
        urls = super(OrganizationDraftAdmin, self).get_urls()
        new_urls = [
            url(r'^check_organization_draft/(?P<draft_id>\d+)/$',
                admin_views.check_organization_draft,
                name="organization_organizationdraft_check_organization_draft"),
        ]

        return new_urls + urls

    def check_organization_draft(self, obj):
        """
        Display a link to review the organization draft and possibly replace
        the original organization details with it
        """
        link = u"<a href=\"%s\">{0}</a>" % (
            reverse(
                "admin:organization_organizationdraft_check_organization_draft",
                args=[obj.id]))

        if not obj.checked:
            return link.format(_("Review"))
        else:
            link = link.format(_("Review again"))
            if obj.updated:
                return u"{0} - {1}".format(link, _("Updated"))
            else:
                return u"{0} - {1}".format(link, _("Ignored"))

    check_organization_draft.allow_tags = True


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'organization',
        'message',
        'rating',
    ]
