from django.urls import path

from user.views import CreateUserView, CreateTokenView, UserManageView, LogoutView

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UserManageView.as_view(), name="me"),
]
