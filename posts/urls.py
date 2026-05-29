from django.urls import path
from rest_framework import routers

from posts.views import PostViewSet, CommentViewSet

app_name = "posts"

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("comments", CommentViewSet, basename="comment")

urlpatterns = [
    path(
        "posts/<int:post_pk>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="post-comments",
    ),
] + router.urls
