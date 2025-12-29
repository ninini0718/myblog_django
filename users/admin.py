# users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nickname', 'date_of_birth')


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')
    actions = ['ban_users', 'unban_users']

    def ban_users(self, request, queryset):
        queryset.update(is_active=False)
    ban_users.short_description = '封禁所选用户'

    def unban_users(self, request, queryset):
        queryset.update(is_active=True)
    unban_users.short_description = '解除封禁所选用户'
