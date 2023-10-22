from django.contrib import admin

from .models import User, FollowAuthor

admin.site.register(User)


@admin.register(FollowAuthor)
class FollowAuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', )
