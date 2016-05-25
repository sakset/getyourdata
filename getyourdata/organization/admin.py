from django.contrib import admin

from organization.models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
	list_display = [
		'name'
	]

# Register your models here.
