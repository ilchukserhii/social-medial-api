from django.contrib import admin

from posts.models import Post, Tag, Comment


class TagInline(admin.TabularInline):
    model = Tag
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [TagInline,]


admin.site.register(Tag)
admin.site.register(Comment)
