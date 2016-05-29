from django.contrib import admin

from organization.models import Organization, AuthenticationField


@admin.register(AuthenticationField)
class AuthenticationFieldAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'verified'
    ]

