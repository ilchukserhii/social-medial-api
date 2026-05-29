from django.urls import path, include
from rest_framework import routers

from user.views import (
    CreateUserView,
    CreateTokenView,
    UserManageView,
    LogoutView,
    UserPublicView
)

app_name = "user"
router = routers.DefaultRouter()
router.register("users", UserPublicView, basename="users")

urlpatterns = [
    path("auth/register/", CreateUserView.as_view(), name="register"),
    path("auth/login/", CreateTokenView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("users/me/", UserManageView.as_view(), name="me"),
    path("", include(router.urls)),
]
