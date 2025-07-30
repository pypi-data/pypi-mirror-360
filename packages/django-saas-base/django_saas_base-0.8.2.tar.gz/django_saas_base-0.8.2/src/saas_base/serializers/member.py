from django.utils.translation import gettext as _
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from ..drf.serializers import ModelSerializer, RelatedSerializerField
from ..models import Member, UserEmail
from .tenant import TenantSerializer
from .permission import PermissionSerializer
from .group import GroupSerializer
from .user import UserSerializer


class MemberSerializer(ModelSerializer):
    user = UserSerializer(required=False, read_only=True)
    inviter = UserSerializer(required=False, read_only=True)
    groups = GroupSerializer(required=False, many=True, read_only=True)
    permissions = PermissionSerializer(required=False, many=True, read_only=True)

    class Meta:
        model = Member
        exclude = ['tenant']
        request_include_fields = ['user', 'groups', 'permissions']


class MemberInviteSerializer(ModelSerializer):
    invite_email = serializers.EmailField(required=True)
    groups = RelatedSerializerField(GroupSerializer, many=True, required=False)
    permissions = RelatedSerializerField(PermissionSerializer, many=True, required=False)

    class Meta:
        model = Member
        fields = ['invite_email', 'groups', 'permissions']

    def validate_invite_email(self, email: str):
        view = self.context['view']
        tenant_id = view.get_tenant_id()
        if Member.objects.filter(tenant_id=tenant_id, invite_email=email).count():
            raise ValidationError(_('This email has already been invited.'))
        return email

    def create(self, validated_data):
        request = self.context['request']
        email = validated_data['invite_email']
        try:
            user_email = UserEmail.objects.get_by_email(email)
            validated_data['user_id'] = user_email.user_id
            if user_email.user_id == request.user.id:
                validated_data['status'] = Member.InviteStatus.ACTIVE
            else:
                validated_data['status'] = Member.InviteStatus.WAITING
        except UserEmail.DoesNotExist:
            pass
        validated_data['inviter'] = request.user
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise ValidationError({
                'invite_email': [_('This user has already been invited.')],
            })


class MemberDetailSerializer(ModelSerializer):
    groups = RelatedSerializerField(GroupSerializer, many=True)
    permissions = RelatedSerializerField(PermissionSerializer, many=True)

    class Meta:
        model = Member
        exclude = ['tenant', 'user']
        read_only_fields = [
            'inviter',
            'invite_email',
            'created_at',
        ]


class UserMembershipSerializer(ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Member
        exclude = ['user', 'inviter', 'invite_email']
        read_only_fields = [
            'inviter',
            'invite_email',
            'created_at',
        ]
        request_include_fields = ['groups', 'permissions']

    def validate_status(self, status):
        # user agree to join the tenant
        if status != Member.InviteStatus.ACTIVE:
            raise ValidationError(_('Invalid status value.'))
        return status
