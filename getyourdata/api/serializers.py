from rest_framework import serializers
from organization.models import Organization

class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'verified', 'accepts_email', 'accepts_mail',)
