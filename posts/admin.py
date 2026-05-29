from django.contrib import admin

from posts.models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    filter_horizontal = ("tags",)


admin.site.register(Tag)
admin.site.register(Comment)
