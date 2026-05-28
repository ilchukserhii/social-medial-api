from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from posts.models import Post
from posts.serializers import PostCreateSerializer, PostListSerializer
from user.models import User


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            Post.objects.all().
            select_related("author").
            prefetch_related("tags", "likes")
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
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
