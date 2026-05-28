from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from posts.serializers import PostCreateSerializer, PostListSerializer, PostDetailSerializer

from posts.models import Post, Tag, Comment

POST_URL = reverse("posts:post-list")
COMMENT_URL = reverse("posts:comment-list")

def detail_url(post_id):
    return reverse("posts:post-detail", args=[post_id])

def sample_user(**params):
    defaults = {
        "email": "user@email.com",
        "password": "password",
        "nickname": "author",
        "first_name": "user1",
        "last_name": "user2",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)

def sample_post(**params):
    author = params.pop("author", None) or sample_user()
    defaults = {
        "title": "title",
        "content": "content",
        "author": author,
        "is_published": True,
    }
    defaults.update(params)

    tags = defaults.pop("tags", [])

    post = Post.objects.create(**defaults)

    if tags:
        post.tags.set(tags)
    return post


class PostModelTest(TestCase):
    def test_published_post(self):
        post = sample_post()
        post.save()
        post.refresh_from_db()
        self.assertIsNotNone(post.published_at)
        self.assertAlmostEqual(
            post.published_at,
            timezone.now(),
            delta=timezone.timedelta(seconds=1),
        )


class PostSerializerTest(TestCase):
    def test_create_post_without_scheduled_at_sets_is_published_true(self):
        tag = Tag.objects.create(name="test")
        user = sample_user(email="author@email.com", nickname="author")

        serializer = PostCreateSerializer(data={
            "title": "Test post",
            "content": "Test content",
            "tags": ["test"],
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)

        post = serializer.save(author=user)

        self.assertTrue(post.is_published)
        self.assertIsNotNone(post.published_at)
        self.assertIn(tag, post.tags.all())

class UnauthorizedPostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(POST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthorizedPostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="email.com",
            password="password",
            nickname="user",
        )
        self.client.force_authenticate(self.user)

    def test_post_list(self):
        tag = Tag.objects.create(name="test")
        post = sample_post(tags=[tag])
        author2 = sample_user(
            email="user1@email.com",
            nickname="author2"
        )
        post_2 = sample_post(
            title="title2",
            content="content2",
            author=author2,
            tags=[tag],
        )

        response = self.client.get(POST_URL)
        posts = Post.objects.all().order_by("-published_at")
        serializer = PostListSerializer(posts, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_post_detail(self):
        tag = Tag.objects.create(name="test")
        post = sample_post(tags=[tag])

        response = self.client.get(detail_url(post.pk))

        serializer = PostDetailSerializer(post)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_post_detail_can_be_edited_only_author(self):
        post = sample_post()

        payload = {
            "title": "title2",
            "content": "content2",
        }

        response = self.client.patch(detail_url(post.pk), payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_owner(self):
        post = sample_post(author=self.user)

        response = self.client.get(POST_URL, {"owner": "true"})
        serializer = PostListSerializer(post)
        self.assertEqual(
            serializer.data["author"],
            response.data["results"][0]["author"]
        )

    def test_filter_by_following(self):
        author = sample_user(
            email="author@email.com",
            nickname="author",
        )
        self.user.following.add(author)
        post = sample_post(author=author)
        response = self.client.get(
            POST_URL,
            {"following": "true"}
        )
        serializer = PostListSerializer([post], many=True)
        self.assertEqual(
            serializer.data,
            response.data["results"]
        )

    def test_filter_by_tags(self):
        tag = Tag.objects.create(name="test")
        post = sample_post(tags=[tag])
        post_2 = sample_post(author=self.user)
        response = self.client.get(
            POST_URL,
            {"tag": "test"}
        )
        serializer = PostListSerializer(post)
        serializer_2 = PostDetailSerializer(post_2)
        self.assertIn(serializer.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_filter_by_title(self):
        post = sample_post()
        post_2 = sample_post(title="title2", author=self.user)
        response = self.client.get(
            POST_URL,
            {"title": "title2"}
        )
        serializer = PostListSerializer(post)
        serializer_2 = PostListSerializer(post_2)
        self.assertIn(serializer_2.data, response.data["results"])
        self.assertNotIn(serializer.data, response.data["results"])

    def test_filter_by_content(self):
        post = sample_post(content="hello text")
        post_2 = sample_post(author=self.user, content="another text")
        response = self.client.get(
            POST_URL,
            {"content": "hello"}
        )
        serializer = PostListSerializer(post)
        serializer_2 = PostListSerializer(post_2)
        self.assertIn(serializer.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_filter_by_author(self):
        author = sample_user(nickname="johndoe")
        post = sample_post(author=author)
        post_2 = sample_post(author=self.user)
        response = self.client.get(
            POST_URL,
            {"author": "johndoe"}
        )
        serializer = PostListSerializer(post)
        serializer_2 = PostListSerializer(post_2)
        self.assertIn(serializer.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_filter_by_liked_posts(self):
        post = sample_post()
        post_2 = sample_post(author=self.user)
        post.likes.add(self.user)
        response = self.client.get(
            POST_URL,
            {"liked": "true"}
        )
        serializer = PostListSerializer(post)
        serializer_2 = PostListSerializer(post_2)
        self.assertIn(serializer.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])

    def test_like_post(self):
        post = sample_post()
        post_2 = sample_post(author=self.user)
        response = self.client.post(
            reverse("posts:post-like", args=[post.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(post.likes.filter(id=self.user.id).exists())

    def test_like_twice_unavailable_post(self):
        post = sample_post()
        post_2 = sample_post(author=self.user)
        post.likes.add(self.user)
        response = self.client.post(
            reverse("posts:post-like", args=[post.id])
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(post.likes.filter(id=self.user.id).exists())

    def test_dislike_post(self):
        post = sample_post(author=self.user)
        post.likes.add(self.user)
        response = self.client.post(
            reverse("posts:post-dislike", args=[post.id])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(post.likes.filter(id=self.user.id).exists())

    def test_dislike_when_no_like_unavailable_post(self):
        post = sample_post(author=self.user)
        response = self.client.post(
            reverse("posts:post-dislike", args=[post.id])
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(post.likes.filter(id=self.user.id).exists())

    def test_filter_by_scheduled_posts(self):
        future_time = timezone.now() + timedelta(hours=1)
        post = sample_post(
            is_published=False,
            scheduled_at=future_time,
            author=self.user
        )
        post_2 = sample_post()

        response = self.client.get(
            POST_URL,
            {"scheduled": "true"}
        )
        serializer = PostListSerializer(post)
        serializer_2 = PostListSerializer(post_2)
        self.assertIn(serializer.data, response.data["results"])
        self.assertNotIn(serializer_2.data, response.data["results"])


class CommentsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user22@email.com",
            password="password",
            nickname="johndoe"
        )
        self.client.force_authenticate(self.user)

    def test_auth_required_for_comments(self):
        response = self.client.get(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment_assigned_to_user(self):
        post = sample_post()
        payload = {
            "content": "test comment",
            "post": post.title
        }
        response = self.client.post(COMMENT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "test comment")
        self.assertEqual(response.data["author"], self.user.nickname)

    def test_nested_url_comments_assigned_to_post(self):
        post_1 = sample_post()
        post_2 = sample_post(title="second", author=self.user)
        comment_1 = Comment.objects.create(
            post=post_1,
            author=self.user,
            content="comment for post 1",
        )
        comment_2 = Comment.objects.create(
            post=post_2,
            author=self.user,
            content="comment for post 2",
        )
        url = reverse("posts:post-comments", args=[post_1.id])
        response = self.client.get(url)
        self.assertContains(response, comment_1.content)
        self.assertNotContains(response, comment_2.content)

    def test_not_user_comments_cant_be_edited(self):
        user = sample_user(nickname="john", email="john@email.cm")
        post = sample_post(title="second")
        comment = Comment.objects.create(
            post=post,
            author=user,
            content="comment for post",
        )
        url = reverse("posts:comment-detail", args=[comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, {"content": "comment"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
