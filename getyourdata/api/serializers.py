from rest_framework import serializers
from organization.models import Organization, Register


class RegisterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Register
        fields = ('id', 'name')


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):

    registers = RegisterSerializer(source='register_set', many='True')

    class Meta:
        model = Organization
        fields = ('id', 'name', 'verified', 'accepts_email', 'accepts_mail', 'registers')
        depth = 2
