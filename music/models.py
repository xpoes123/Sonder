# models.py

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

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
        return f"{self.name} by {self.artist}"
    
class Cluster(models.Model):
    name = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.name} is {self.genre}"