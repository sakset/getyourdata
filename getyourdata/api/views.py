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
    queryset = Organization.objects.filter(verified=True)
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        queryset = Organization.objects.filter(verified=True)

        organization_name = self.request.query_params.get("name", "")

        if organization_name != "":
            queryset = queryset.filter(name__icontains=organization_name)

        return queryset
