from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ['password', 'groups', 'user_permissions']


class UserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise ValidationError(_('Password incorrect.'))
        return value

    def validate_password(self, raw_password: str):
        if self.initial_data['confirm_password'] != raw_password:
            raise ValidationError(_('Password does not match.'))
        password_validation.validate_password(raw_password)
        return raw_password

    def update(self, user, validated_data):
        raw_password = validated_data['password']
        user.set_password(raw_password)
        user.save()
        return user
