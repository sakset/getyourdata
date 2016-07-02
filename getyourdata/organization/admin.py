from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from organization.models import Organization, OrganizationDraft
from organization.models import AuthenticationField

from organization import admin_views

@admin.register(AuthenticationField)
class AuthenticationFieldAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_on',
    ]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'verified',
        'created_on',
        'updated_on',
    ]


@admin.register(OrganizationDraft)
class OrganizationDraftAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'verified',
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
        if not obj.checked:
            return "<a href=\"%s\">%s</a>" % (
                reverse("admin:organization_organizationdraft_check_organization_draft",
                    args=[obj.id]),
                _("Check draft"))
        else:
            if obj.updated:
                return _("Updated")
            else:
                return _("Ignored")
    check_organization_draft.allow_tags = True
