from rest_framework import serializers
from organization.models import Organization, Register, Comment

# future expansion to support multiple registers per organization
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = ('id', 'name')


# future expansion to enable displaying of all ratings/comments on organization list page
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('rating', 'message')


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):

    registers = serializers.StringRelatedField(many=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = (
            'id',
            'name',
            'verified',
            'accepts_email',
            'accepts_mail',
            'address_line_one',
            'address_line_two',
            'postal_code',
            'country',
            'email_address',
            'registers',
            'average_rating',
            'amount_ratings',
            'comments',
        )
        depth = 2
