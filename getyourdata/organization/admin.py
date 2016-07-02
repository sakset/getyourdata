from django.contrib import admin

from organization.models import Organization, OrganizationDraft
from organization.models import AuthenticationField


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
        'created_on',
        'updated_on',
    ]
