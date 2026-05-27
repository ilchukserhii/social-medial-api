from django.urls import path, include
from rest_framework import routers

from user.views import CreateUserView, CreateTokenView, UserManageView, LogoutView, UserPublicView

app_name = "user"
router = routers.DefaultRouter()
router.register("other-users", UserPublicView)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UserManageView.as_view(), name="me"),
    path("", include(router.urls)),
]
