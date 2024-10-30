# music/services/spotify_service.py

import json
import os
from dotenv import load_dotenv
import base64
from requests import post, get
import random
import gemini  # Ensure this is installed or handle appropriately

from django.conf import settings

class Song:
    def __init__(self, song_id, name, artist, stats, image, preview):
        self.song_id = song_id
        self.name = name
        self.artist = artist
        self.stats = stats
        self.image = image
        self.preview = preview
        self.dating_profile = None  # To be added later

def printj(json_file):
    print(json.dumps(json_file, indent=4))

def get_token():
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = result.json()
    token = json_result.get("access_token")
    return token

token = get_token()

def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = result.json()["artists"]["items"]
    if not json_result:
        print("No artist exists with this name")
        return None
    return json_result[0]["id"]

def get_related_artist(token, artist_id, limit=3):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()
    related_artists = json_result.get('artists', [])[:limit]
    return related_artists

def get_artist_tracks(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()
    return json_result["tracks"]

# Returns the song's image, name, artist, preview_url, and stats
def get_song_info(song_id):
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()
    image = get_song_image(json_result)
    name = get_song_name(json_result)
    artist_name = get_song_artist_name(json_result)
    preview_url = get_song_preview(json_result)
    stats = get_song_stats(song_id)
    if not preview_url:
        return 0
    return image, name, artist_name, preview_url, stats

def get_dating_profile(song):
    return gemini.get_dating_profile(song.name, song.artist[0], song.stats)

def get_song_stats(song_id):
    url = f"https://api.spotify.com/v1/audio-features/{song_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()
    acoustic = json_result["acousticness"]
    dance = json_result["danceability"]
    duration = json_result["duration_ms"]
    energy = json_result["energy"]
    instrumental = json_result["instrumentalness"]
    key = json_result["key"]
    liveness = json_result["liveness"]
    loud = json_result["loudness"]
    mode = json_result["mode"]
    speech = json_result["speechiness"]
    tempo = json_result["tempo"]
    valence = json_result["valence"]
    return acoustic, dance, duration, energy, instrumental, key, liveness, loud, mode, speech, tempo, valence

def get_song_artist_name(song_json):
    return [artist["name"] for artist in song_json["artists"]]

def get_song_preview(song_json):
    return song_json.get("preview_url")

def get_song_name(song_json):
    return song_json["name"]

def get_song_image(song_json):
    return song_json["album"]["images"][1]['url'] if len(song_json["album"]["images"]) > 1 else song_json["album"]["images"][0]['url']

def get_songs_from_seed(artist_seed, limit = 1):
    url = "https://api.spotify.com/v1/recommendations"
    query = ""
    if artist_seed:
        query += f"seed_artists={artist_seed}&limit={limit}"
    url += f"?{query}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()
    return json_result.get("tracks", [])

def recommend_seed(song_seed, artist_seed):
    songs = get_songs_from_seed(song_seed, artist_seed)
    song_infos = []
    for track in songs:
        song_info = get_song_info(track["id"])
        if song_info == 0:
            continue
        song = Song(song_id=track["id"], name=song_info[1], image=song_info[0],
                    artist=song_info[2], preview=song_info[3], stats=song_info[4])
        song_infos.append(song)
    random.shuffle(song_infos)
    return song_infos

def generate_artist_seed(artist_list):
    ids = [search_for_artist(token, artist) for artist in artist_list]
    artist_seed = ",".join(filter(None, ids))
    return artist_seed

def process_lists(artist_list):
    artist_seed = generate_artist_seed(artist_list)
    tracks = get_songs_from_seed(artist_seed)

    song_objects = []
    for track in tracks:
        song_info = get_song_info(track["id"])
        if song_info == 0:
            continue
        song = Song(
            song_id=track["id"],
            name=song_info[1],
            artist=song_info[2],
            stats=song_info[4],
            image=song_info[0],
            preview=song_info[3]
        )
        song_objects.append(song)

    random.shuffle(song_objects)
    return song_objects
