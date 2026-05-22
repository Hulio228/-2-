from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Location, Post

User = get_user_model()

admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Comment)

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, UserAdmin)
