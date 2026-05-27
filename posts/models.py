# from django.db import models
#
# from social_media_api import settings
#
#
# class Post(models.Model):
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     author = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="posts",
#     )
#     tags = models.ManyToManyField(
#         "Tags",
#         blank=True,
#         null=True,
#         related_name="posts",
#     )
