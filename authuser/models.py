# authuser/models.py

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import JSONField

class CustomUserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a User with the given username, email, and password.
        """
        if not username:
            raise ValueError("The username field is required")
        if not email:
            raise ValueError("You have not provided a valid email address")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Create and save a regular User with the given username, email, and password.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given username, email, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Validate superuser flags
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, default="")
    email = models.EmailField(blank=True, default="", unique=True)
    name = models.CharField(max_length=255, blank=True, default="")
    
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    # Relationships to songs
    liked_songs = models.ManyToManyField('music.Song', related_name='liked_by_users', blank=True)
    disliked_songs = models.ManyToManyField('music.Song', related_name='disliked_by_users', blank=True)
    
    liked_song_count = models.IntegerField(default=0)
    disliked_song_count = models.IntegerField(default=0)

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name or self.username
    
    def increment_liked_song_count(self):
        """Increments the liked song count and checks if recommendations should run."""
        self.liked_song_count += 1
        self.save()
        return self.liked_song_count

    def increment_disliked_song_count(self):
        """Increments the disliked song count."""
        self.disliked_song_count += 1
        self.save()
        return self.disliked_song_count
    
    def get_song_count(self):
        return self.disliked_song_count + self.liked_song_count
    
class UserCluster(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, related_name='user_cluster')
    liked_clusters = JSONField(blank=True, null=True)  # Store liked clusters as JSON
    disliked_clusters = JSONField(blank=True, null=True)  # Store disliked clusters as JSON

    def __str__(self):
        return f"Cluster data for {self.user.username}"
