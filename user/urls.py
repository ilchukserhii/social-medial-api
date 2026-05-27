from django.urls import path

from user.views import CreateUserView, CreateTokenView, UserManageView

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("me/", UserManageView.as_view(), name="me"),
]
