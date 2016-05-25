from django.shortcuts import render

from organization.models import Organization

# Create your views here.


def list_organizations(request):
	organizations = Organization.objects.all()
	return render(request, 'organization/list.html', {
		'organizations':organizations
		})