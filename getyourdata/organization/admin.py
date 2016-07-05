from django.contrib import admin

from organization.models import Organization, AuthenticationField, Register


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

@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_on',
    ]
