from django.contrib.auth import get_user_model
from rest_framework import generics, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from user.serializers import UserCreateSerializer, UserManagerSerializer, UserPublicSerializer

User = get_user_model()

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserManageView(generics.RetrieveUpdateAPIView):
    serializer_class = UserManagerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
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
    serializer_class = UserPublicSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        nickname = self.request.query_params.get("nickname")
        queryset = User.objects.all()

        if nickname:
            queryset = self.queryset.filter(nickname__icontains=nickname)

        return queryset
