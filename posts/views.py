from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from posts.models import Post, Comment
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import PostCreateSerializer, PostListSerializer, CommentSerializer, PostDetailSerializer


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
            queryset = queryset.filter(likes__isnull=False)

        if scheduled == "true":
            queryset = queryset.filter(
                author=self.request.user,
                is_published=False,
                scheduled_at__isnull=False
            )
        else:
            queryset = queryset.filter(is_published=True)

        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PostCreateSerializer
        elif self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        put_like = self.get_object()
        if put_like.likes.filter(nickname=request.user.nickname).exists():
            return Response(
                {"detail": "You have already liked this post."},
                status=400
            )
        put_like.likes.add(request.user)
        return Response({"detail": "You have liked this post."})

    @action(detail=True, methods=["post"])
    def dislike(self, request, pk=None):
        dislike = self.get_object()
        if dislike.likes.filter(nickname=request.user.nickname).exists():
            dislike.likes.remove(request.user)
            return Response({"detail": "You have disliked this post."})
        return Response(
            {"detail": "You have not liked this post."},
            status=400
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.select_related(
            "author",
            "post",
            "post__author"
        )

        post_pk = self.kwargs.get("post_pk")
        if post_pk:
            queryset = queryset.filter(post_id=post_pk)

        return queryset

    def perform_create(self, serializer):
        post_pk = self.kwargs.get("post_pk")

        if post_pk:
            serializer.save(author=self.request.user, post_id=post_pk)
        else:
            serializer.save(author=self.request.user)
