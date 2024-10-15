from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'role', 'first_name', 'last_name', 'username', 'password', 'last_login')
        read_only_fields = ('last_login',)
        extra_kwargs = {'password': {'write_only': True}}
        model = User

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user

    def validate(self, data):
        role = data.get('role', None)
        if role not in [1, 2]:
            raise ValidationError({"message": "Role can be only 1 and 2"}, code=400)
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100, required=True)
    new_password = serializers.CharField(max_length=100, required=True)

    def validate(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if old_password == new_password:
            raise ValidationError({'message': 'New password cannot be the same with old one'}, code=400)
        return data
