from django.shortcuts import render
from rest_framework import permissions, renderers, viewsets

from organization.models import Organization
from api.serializers import OrganizationSerializer

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    List of verified organizations exposed through a REST API for use with
    improved organization list view, which allows filtering and selecting
    multiple organizations
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
