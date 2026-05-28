from django.contrib.admin import actions
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.template.defaultfilters import first
from django.views.generic import detail
from rest_framework import generics, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from user.models import User
from user.serializers import (
    UserCreateSerializer,
    UserManagerSerializer,
    UserPublicListSerializer,
    UserPublicDetailSerializer
)

User = get_user_model()

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserManageView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserManagerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out"}, status=200)


class UserPublicView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        nickname = self.request.query_params.get("nickname")
        name = self.request.query_params.get("name")
        queryset = User.objects.all()

        if nickname:
            queryset = self.queryset.filter(nickname__icontains=nickname)

        if name:
            queryset = self.queryset.filter(
                Q(first_name__icontains=name) |
                Q(last_name__icontains=name)
            )

        return queryset.order_by("-date_joined")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserPublicDetailSerializer
        return UserPublicListSerializer

    @action(detail=True, methods=["post"])
    def follow(self, request, pk=None):
        user_to_follow = self.get_object()
        if user_to_follow == request.user:
            return Response({"message": "You cannot follow yourself"}, status=400)
        if request.user.following.filter(pk=user_to_follow.id).exists():
            return Response({"message": "You`re already following this user"})
        request.user.following.add(user_to_follow)
        return Response({"message": "You`re now following this user"})

    @action(detail=True, methods=["post"])
    def unfollow(self, request, pk=None):
        user_to_unfollow = self.get_object()
        if request.user.following.filter(pk=user_to_unfollow.id).exists():
            request.user.following.remove(user_to_unfollow)
            return Response({"message": "You`re not following this user anymore"})
        return Response({"message": "You`re not following this user"})


