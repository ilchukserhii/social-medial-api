from django.contrib.auth import get_user_model
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
    following = serializers.SlugRelatedField(
        slug_field="email",
        many=True,
        read_only=True,
    )
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "nickname",
            "first_name",
            "last_name",
            "profile_pic",
            "phone",
            "birth_date",
            "bio",
            "following",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False,
                "allow_blank": True,
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


class UserPublicListSerializer(serializers.ModelSerializer):
    following = serializers.IntegerField(
        read_only=True,
        source="following.count"
    )
    followers = serializers.IntegerField(
        read_only=True,
        source="followers.count"
    )
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "nickname",
            "first_name",
            "last_name",
            "profile_pic",
            "bio",
            "following",
            "followers",
        )

class UserPublicDetailSerializer(UserPublicListSerializer):
    following_list = serializers.SerializerMethodField()
    followers_list = serializers.SerializerMethodField()
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "nickname",
            "first_name",
            "last_name",
            "profile_pic",
            "bio",
            "following",
            "following_list",
            "followers",
            "followers_list",
        )

    def get_following_list(self, obj):
        following_list = obj.following.all()[:10]

        return [
            following.nickname or str(following)
            for following in following_list
        ]

    def get_followers_list(self, obj):
        followers_list = obj.followers.all()[:10]

        return [
            follower.nickname or str(follower)
            for follower in followers_list
        ]
