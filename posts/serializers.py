from rest_framework import serializers

from posts.models import Tag, Comment, Post


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="nickname", read_only=True)
    post = serializers.SlugRelatedField(slug_field="title", read_only=True)
    class Meta:
        model = Comment
        fields = ("id", "content", "author", "post", "created_at")


class PostListSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    likes = serializers.IntegerField(read_only=True, source="likes.count")
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
            "likes",
            "created_at"
        )

    def get_tags(self, obj):
        list_tags = obj.tags.all()

        return [
            tag.name for tag in list_tags
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