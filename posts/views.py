from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from posts.models import Post, Comment
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import (
    PostCreateSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentWriteSerializer,
    CommentReadSerializer
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def get_queryset(self):
        owner = self.request.query_params.get("owner")
        following = self.request.query_params.get("following")
        tag = self.request.query_params.get("tag")
        title = self.request.query_params.get("title")
        content = self.request.query_params.get("content")
        author = self.request.query_params.get("author")
        liked = self.request.query_params.get("liked")
        scheduled = self.request.query_params.get("scheduled")
        queryset = (
            Post.objects
            .select_related("author")
            .prefetch_related("tags", "likes", "comments")
        )

        if owner == "true":
            queryset = queryset.filter(author=self.request.user)

        if following == "true":
            queryset = queryset.filter(author__followers=self.request.user)

        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)

        if title:
            queryset = queryset.filter(title__icontains=title)

        if content:
            queryset = queryset.filter(content__icontains=content)

        if author:
            queryset = queryset.filter(author__nickname__icontains=author)

        if liked == "true":
            queryset = queryset.filter(likes=self.request.user)

        if scheduled == "true":
            queryset = queryset.filter(
                author=self.request.user,
                is_published=False,
                scheduled_at__isnull=False
            )
        else:
            queryset = queryset.filter(is_published=True)

        return queryset.order_by("-published_at")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PostCreateSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="owner",
                type=OpenApiTypes.BOOL,
                description="Filter list of posts by owner "
                            "(ex. ?owner=true)"
            ),
            OpenApiParameter(
                name="following",
                type=OpenApiTypes.BOOL,
                description="Filter list of posts by following users "
                            "(ex. ?following=true)"
            ),
            OpenApiParameter(
                name="tag",
                type=OpenApiTypes.STR,
                description="Filter list of posts by tag name "
                            "(ex. ?tag=something)"
            ),
            OpenApiParameter(
                name="title",
                type=OpenApiTypes.STR,
                description="Filter list of posts by title "
                            "(ex. ?title=something)"
            ),
            OpenApiParameter(
                name="content",
                type=OpenApiTypes.STR,
                description="Filter list of posts by content "
                            "(ex. ?content=something)"
            ),
            OpenApiParameter(
                name="author",
                type=OpenApiTypes.STR,
                description="Filter list of posts by author nickname "
                            "(ex. ?author=CrazyAuthor)"
            ),
            OpenApiParameter(
                name="liked",
                type=OpenApiTypes.BOOL,
                description="Filter list of posts by liked posts "
                            "(ex. ?liked=true)"
            ),
            OpenApiParameter(
                name="scheduled",
                type=OpenApiTypes.BOOL,
                description="Filter list of posts by scheduled posts "
                            "(ex. ?scheduled=true)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                description="You have liked this post",
            ),
            400: OpenApiResponse(
                description="You have already liked this post",
            )
        },
        description="Like post by id"
    )
    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        put_like = self.get_object()
        if put_like.likes.filter(pk=request.user.pk).exists():
            return Response(
                {"detail": "You have already liked this post."},
                status=400
            )
        put_like.likes.add(request.user)
        return Response({"detail": "You have liked this post."})

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                description="You have disliked this post",
            ),
            400: OpenApiResponse(
                description="You have not liked this post",
            )
        },
        description="Dislike post by id"
    )
    @action(detail=True, methods=["post"])
    def dislike(self, request, pk=None):
        dislike = self.get_object()
        if dislike.likes.filter(pk=request.user.pk).exists():
            dislike.likes.remove(request.user)
            return Response({"detail": "You have disliked this post."})
        return Response(
            {"detail": "You have not liked this post."},
            status=400
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def get_queryset(self):
        queryset = Comment.objects.select_related(
            "author",
            "post",
            "post__author"
        )

        post_pk = self.kwargs.get("post_pk")
        if post_pk:
            queryset = queryset.filter(post_id=post_pk)

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CommentWriteSerializer
        return CommentReadSerializer

    def perform_create(self, serializer):
        post_pk = self.kwargs.get("post_pk")

        if post_pk:
            serializer.save(author=self.request.user, post_id=post_pk)
        else:
            serializer.save(author=self.request.user)
