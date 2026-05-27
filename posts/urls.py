from django.urls import include, path
from rest_framework import routers

from posts.views import PostViewSet

app_name = "posts"

router = routers.DefaultRouter()
router.register("posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
