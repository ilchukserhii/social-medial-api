import pathlib
import uuid

from django.db import models

from social_media_api import settings


def upload_to(instance, filename):
    title_name = instance.title

    filename = (
        f"{title_name}{uuid.uuid4()}{pathlib.Path(filename).suffix}"
    )

    return pathlib.Path(f"uploads/{title_name}/") / filename


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
        related_name="posts",
    )
    image = models.ImageField(
        upload_to=upload_to,
        null=True,
        blank=True,
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="likes",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} {str(self.author)} {self.created_at}"


class Tag(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
