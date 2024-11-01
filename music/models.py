# models.py

from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255, null=True, blank=True)
    acoustic = models.FloatField()
    dance = models.FloatField()
    duration = models.IntegerField()
    energy = models.FloatField()
    instrumental = models.FloatField()
    key = models.IntegerField()
    liveness = models.FloatField()
    loud = models.FloatField()
    mode = models.IntegerField()
    speech = models.FloatField()
    tempo = models.FloatField()
    valence = models.FloatField()
    popularity = models.FloatField(null=True)
    dating_profile = models.JSONField(null=True, blank=True)
    image = models.URLField(max_length=500, blank=True, null=True)
    preview = models.URLField(max_length=500, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

class UserLikedSongs(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    liked_songs = models.JSONField(default=list)  # Stores a list of Spotify song IDs

    def __str__(self):
        return f"{self.user.username}'s liked songs"

    def add_song(self, spotify_id):
        """Add a song ID to liked songs if it's not already present."""
        if spotify_id not in self.liked_songs:
            self.liked_songs.append(spotify_id)
            self.save()

    def remove_song(self, spotify_id):
        """Remove a song ID from liked songs if it exists."""
        if spotify_id in self.liked_songs:
            self.liked_songs.remove(spotify_id)
            self.save()

    def is_song_liked(self, spotify_id):
        """Check if a song ID is in liked songs."""
        return spotify_id in self.liked_songs
    
class UserDislikedSongs(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    disliked_songs = models.JSONField(default=list)  # Stores a list of Spotify song IDs

    def __str__(self):
        return f"{self.user.username}'s disliked songs"

    def add_song(self, spotify_id):
        """Add a song ID to liked songs if it's not already present."""
        if spotify_id not in self.disliked_songs:
            self.disliked_songs.append(spotify_id)
            self.save()

    def remove_song(self, spotify_id):
        """Remove a song ID from liked songs if it exists."""
        if spotify_id in self.disliked_songs:
            self.disliked_songs.remove(spotify_id)
            self.save()

    def is_song_disliked(self, spotify_id):
        """Check if a song ID is in liked songs."""
        return spotify_id in self.disliked_songs