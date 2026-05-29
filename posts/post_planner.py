from django.utils import timezone

from posts.models import Post


def post_planner():
    posts = Post.objects.filter(
        is_published=False,
        scheduled_at__isnull=False,
        scheduled_at__lte=timezone.now()
    )

    for post in posts:
        post.is_published = True
        post.save()
