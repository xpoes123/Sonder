from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, UserCluster
from music.models import Song
from django.utils.translation import gettext_lazy as _

# Inline for Liked Songs
class LikedSongsInline(admin.TabularInline):
    model = User.liked_songs.through  # Access through the intermediary table
    extra = 0  # No extra empty fields displayed
    verbose_name = "Liked Song"
    verbose_name_plural = "Liked Songs"

# Inline for Disliked Songs
class DislikedSongsInline(admin.TabularInline):
    model = User.disliked_songs.through
    extra = 0
    verbose_name = "Disliked Song"
    verbose_name_plural = "Disliked Songs"

class CustomUserAdmin(BaseUserAdmin):
    # Specify the fields to be displayed in the admin panel
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    list_display = ('username', 'email', 'name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'name')
    ordering = ('username',)

    # Register inlines with the User admin
    inlines = [LikedSongsInline, DislikedSongsInline]

# Register the custom User model and unregister the Group model if not needed
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)  # Optional, only if you don't need the Group model in admin

class UserClusterAdmin(admin.ModelAdmin):
    list_display = ('user', 'liked_clusters', 'disliked_clusters')
    search_fields = ('user__username',)

admin.site.register(UserCluster, UserClusterAdmin)