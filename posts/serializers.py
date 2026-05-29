from rest_framework import serializers

from posts.models import Tag, Comment, Post


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class CommentReadSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="nickname",
        read_only=True
    )
    post = serializers.SlugRelatedField(
        slug_field="title",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ("id", "content", "author", "post", "created_at")


class CommentWriteSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="nickname",
        read_only=True
    )
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
    )

    class Meta:
        model = Comment
        fields = ("id", "content", "author", "post", "created_at")


class PostListSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
        many=True
    )
    likes = serializers.IntegerField(read_only=True, source="likes.count")
    author = serializers.SlugRelatedField(
        slug_field="nickname",
        read_only=True
    )
    comments = serializers.IntegerField(
        read_only=True,
        source="comments.count"
    )

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
            "published_at"
        )


class PostDetailSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
        many=True
    )
    likes = serializers.IntegerField(read_only=True, source="likes.count")
    author = serializers.SlugRelatedField(
        slug_field="nickname",
        read_only=True
    )
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
            "published_at"
        )

    def get_comments(self, obj):
        comments = obj.comments.all()

        return [
            {
                "author": comment.author.nickname,
                "content": comment.content,
            }
            for comment in comments
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Tag.objects.all(),
        many=True,
        required=False
    )
    author = serializers.SlugRelatedField(
        slug_field="nickname",
        read_only=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "author",
            "tags",
            "image",
            "scheduled_at"
        )

    def create(self, validated_data):
        if validated_data.get("scheduled_at") is None:
            validated_data["is_published"] = True

        return super().create(validated_data)
