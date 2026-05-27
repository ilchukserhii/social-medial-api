from django.contrib.auth import get_user_model
from django.db.models import Model
from rest_framework import serializers


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
                "min_length": 8,
            }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

class UserManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "profile_pic",
            "phone",
            "birth_date",
            "bio"
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
                "min_length": 8,
            }
        }

        def update(self, instance, validated_data):
            password = validated_data.pop("password", None)
            user = super().update(instance, validated_data)

            if password:
                user.set_password(password)
                user.save()

            return user