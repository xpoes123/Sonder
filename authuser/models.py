# authuser/models.py

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone

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
