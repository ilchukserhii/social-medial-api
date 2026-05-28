from django.template.defaulttags import comment
from rest_framework import serializers

from posts.models import Tag, Comment, Post


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    post = serializers.SlugRelatedField(
        slug_field="title",
        queryset=Post.objects.all(),
    )
    class Meta:
        model = Comment
        fields = ("id", "content", "author", "post", "created_at")


class PostListSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    likes = serializers.IntegerField(read_only=True, source="likes.count")
    author = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    comments = serializers.IntegerField(read_only=True, source="comments.count")
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author",
            "tags",
            "image",
            "likes",
            "comments",
            "created_at"
        )


class PostDetailSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    likes = serializers.IntegerField(read_only=True, source="likes.count")
    author = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author",
            "tags",
            "image",
            "likes",
            "comments",
            "created_at"
        )

    def get_comments(self, obj):
        comments = obj.comments.all()

        return [
            {comment.author.nickname: comment.content for comment in comments}
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )
    author = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author",
            "tags",
            "image",
            "created_at"
        )