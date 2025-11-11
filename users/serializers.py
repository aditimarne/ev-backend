# users/serializers.py

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from mongoengine.errors import NotUniqueError


from .models import User


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match."})

        if User.objects(username=data['username']).first():
            raise serializers.ValidationError({"username": "Username already exists."})

        if User.objects(email=data['email']).first():
            raise serializers.ValidationError({"email": "Email already exists."})

        return data


    def create(self, validated_data):
        validated_data.pop('password2')
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password'])
        )
        user.save()
        return user



# ✅ Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid username or password")

        data['user'] = user
        return data

# users/serializers.py

class ProfileSerializer(serializers.Serializer):
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    mobile = serializers.CharField(required=False, allow_blank=True)
    profile_image = serializers.CharField(read_only=True)   # ✅ Add this
    avatar_file_id = serializers.CharField(read_only=True)   # ✅ Add this
    avatar_url = serializers.SerializerMethodField(read_only=True)

    def get_avatar_url(self, obj):
        if obj.avatar_file_id:
            return f"/api/avatar/{obj.avatar_file_id}/"
        return None

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.mobile = validated_data.get("mobile", instance.mobile)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, data):
        return data