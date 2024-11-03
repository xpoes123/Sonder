from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, UserCluster
from music.models import Song
from django.utils.translation import gettext_lazy as _

class LikedSongsInline(admin.TabularInline):
    model = User.liked_songs.through
    extra = 0
    verbose_name = "Liked Song"
    verbose_name_plural = "Liked Songs"

class DislikedSongsInline(admin.TabularInline):
    model = User.disliked_songs.through
    extra = 0
    verbose_name = "Disliked Song"
    verbose_name_plural = "Disliked Songs"

# Creating a custom user 
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

    inlines = [LikedSongsInline, DislikedSongsInline]

# Register the custom User model
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)

class UserClusterAdmin(admin.ModelAdmin):
    list_display = ('user', 'liked_clusters', 'disliked_clusters')
    search_fields = ('user__username',)

admin.site.register(UserCluster, UserClusterAdmin)