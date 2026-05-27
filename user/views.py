from rest_framework import generics

from user.serializers import UserCreateSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
