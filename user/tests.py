from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from user.models import User
from user.serializers import UserManagerSerializer, UserPublicListSerializer, UserPublicDetailSerializer


PUBLIC_LIST_URL = reverse("user:users-list")

def public_detail_url(user_id):
    return reverse("user:users-detail", args=[user_id])

def sample_public_user(**params):
    defaults = {
        "email": "user1@email.com",
        "password": "password",
        "nickname": "user1",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


class UserModelTest(TestCase):
    def test_user_creation_with_email(self):
        user = get_user_model().objects.create_user(
            email="user@email.com",
            password="password",
        )
        user.refresh_from_db()
        self.assertEqual(user.email, "user@email.com")
        self.assertTrue(user.check_password("password"))
        self.assertIsNone(user.username)


class UserCreateLoginLogoutViewTest(APITestCase):
    def test_create_user(self):
        payload = {
            "email": "user@user.com",
            "password": "password",
        }
        response = self.client.post(reverse("user:register"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_create_token_for_user(self):
        user = get_user_model().objects.create_user(
            email="user@email.com",
            password="password",
        )
        payload = {
            "username": "user@email.com",
            "password": "password",
        }
        response = self.client.post(reverse("user:login"), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        token = Token.objects.get(user=user)
        self.assertEqual(token.key, response.data["token"])

    def test_delete_token_after_logout(self):
        user = get_user_model().objects.create_user(
            email="user@email.com",
            password="password",
        )
        payload = {
            "username": "user@email.com",
            "password": "password",
        }
        login_response = self.client.post(reverse("user:login"), payload)
        token = Token.objects.get(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        logout_response = self.client.post(reverse("user:logout"))
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Token.objects.filter(user=user).exists()
        )


class UserManagePublicViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="someuser@email.com",
            password="password",
        )
        self.client.force_authenticate(self.user)

    def test_user_manage_view(self):
        user_1 = get_user_model().objects.create_user(
            email="user1@email.com",
            password="password",
        )
        user_2 = get_user_model().objects.create_user(
            email="user2@email.com",
            password="password2",
        )
        self.user.following.add(user_1)
        user_2.followers.add(self.user)
        response = self.client.get(reverse("user:me"))
        serializer = UserManagerSerializer(self.user)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_manage_update_view(self):
        payload = {"bio": "new bio"}
        response = self.client.patch(reverse("user:me"), payload)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.bio, "new bio")

    def test_user_manage_delete_view(self):
        response = self.client.delete(reverse("user:me"))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            get_user_model().objects.filter(id=self.user.id).exists()
        )

    def test_user_public_list_view(self):
        user_1 = sample_public_user()
        user_2 = get_user_model().objects.create_user(
            email="user2@email.com",
            password="password2",
            first_name="firstname",
        )

        response = self.client.get(PUBLIC_LIST_URL)
        users = User.objects.all().order_by("-date_joined")
        serializer = UserPublicListSerializer(users, many=True)
        self.assertEqual(response.data["results"], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_public_detail_view(self):
        user_1 = sample_public_user()
        response = self.client.get(public_detail_url(user_1.id))
        serializer = UserPublicDetailSerializer(user_1)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_public_by_nickname(self):
        user_1 = sample_public_user()
        user_2 = get_user_model().objects.create_user(
            email="user2@email.com",
            password="password2",
            first_name="firstname",
        )
        response = self.client.get(
            PUBLIC_LIST_URL,
            {"nickname": "user1"},
        )
        serializer_1 = UserPublicListSerializer(user_1)
        serializer_2 = UserPublicListSerializer(user_2)
        self.assertIn(serializer_1.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_filter_public_by_name(self):
        user_1 = sample_public_user()
        user_2 = get_user_model().objects.create_user(
            email="user2@email.com",
            password="password2",
            first_name="firstname",
        )
        response = self.client.get(
            PUBLIC_LIST_URL,
            {"name": "firstname"},
        )
        serializer_1 = UserPublicListSerializer(user_1)
        serializer_2 = UserPublicListSerializer(user_2)
        self.assertIn(serializer_2.data, response.data["results"])
        self.assertNotIn(serializer_1.data, response.data["results"])

    def test_public_user_follow(self):
        user_1 = sample_public_user()
        response = self.client.post(
            reverse(
                "user:users-follow",
                args=[user_1.id]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user_1.followers.filter(id=self.user.id).exists())

    def test_public_user_cant_follow_self(self):
        response = self.client.post(
            reverse(
                "user:users-follow",
                args=[self.user.id]
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["message"],
            "You cannot follow yourself"
        )

    def test_public_user_cant_follow_twice(self):
        user_1 = sample_public_user()
        response_1 = self.client.post(
            reverse(
                "user:users-follow",
                args=[user_1.id]
            )
        )
        response_2 = self.client.post(
            reverse(
                "user:users-follow",
                args=[user_1.id]
            )
        )
        self.assertEqual(
            response_2.data["message"],
            "You`re already following this user"
        )

    def test_public_user_unfollow(self):
        user_1 = sample_public_user()
        user_1.followers.add(self.user)
        response = self.client.post(reverse("user:users-unfollow", args=[user_1.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
        "You`re not following this user anymore")

    def test_public_user_cant_unfollow_user_that_not_follow(self):
        user_1 = sample_public_user()
        response = self.client.post(reverse("user:users-unfollow", args=[user_1.id]))
        self.assertEqual(
            response.data["message"],
            "You`re not following this user"
        )
