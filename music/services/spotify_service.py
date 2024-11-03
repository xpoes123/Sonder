# music/services/spotify_service.py

import json
import os
from dotenv import load_dotenv
import base64
from requests import post, get
import random
import logging
import gemini

from django.conf import settings

logger = logging.getLogger(__name__)

class Song:
    def __init__(self, song_id, name, artist, stats, image, preview, link):
        self.song_id = song_id
        self.name = name
        self.artist = artist
        self.stats = stats
        self.image = image
        self.preview = preview
        self.link = link
        self.dating_profile = None

def printj(json_file):
    """Debugging tool"""
    print(json.dumps(json_file, indent=4))

def get_token():
    """Obtain an OAuth token for the Spotify API."""
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
    """Get the Spotify header with the provided token"""
    return {"Authorization": f"Bearer {token}"}

def search_for_artist(token, artist_name):
    """Find the artist based on the artist name using the Spotify API."""
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)

    if result.status_code != 200:
        logger.error("Failed to search for artist, status code: %s, response: %s", result.status_code, result.text)
        return None
    json_result = result.json().get("artists", {}).get("items", [])
    if not json_result:
        logger.warning("No artist exists with the name: %s", artist_name)
        return None

    return json_result[0]["id"]

def get_related_artist(token, artist_id, limit=3):
    """Find similar artists based on another artist using the Spotify API"""
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()
    related_artists = json_result.get('artists', [])[:limit]
    return related_artists

def get_artist_tracks(token, artist_id):
    """Find the top songs of an artist using the Spotify API"""
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()
    return json_result["tracks"]

def get_track_link(json_result):
    """Returns the link of a song, helper method"""
    return json_result["album"]["external_urls"]["spotify"]

def get_song_info(song_id):
    """Returns all of the info of a song using the Spotify API"""
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    if result.status_code == 429:
        logger.error("Spotify API rate limit exceeded while fetching song info.")
        return None

    json_result = result.json()
    image = get_song_image(json_result)
    name = get_song_name(json_result)
    artist_name = get_song_artist_name(json_result)
    preview_url = get_song_preview(json_result)
    stats = get_song_stats(song_id)
    link = get_track_link(json_result)
    if not preview_url:
        return 0
    return image, name, artist_name, preview_url, stats, link

def get_dating_profile(song):
    """Creates a dating profile for a song"""
    return gemini.get_dating_profile(song.name, song.artist[0], song.stats)

def get_song_stats(song_id):
    """Returns all of the stats of a song using the Spotify API"""
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
    url_pop = f"https://api.spotify.com/v1/tracks/{song_id}"
    result_pop = get(url_pop, headers=headers)
    json_result_pop = result_pop.json()
    pop = json_result_pop['popularity']
    return acoustic, dance, duration, energy, instrumental, key, liveness, loud, mode, speech, tempo, valence, pop

def get_song_artist_name(song_json):
    return [artist["name"] for artist in song_json["artists"]]

def get_song_preview(song_json):
    return song_json.get("preview_url")

def get_song_name(song_json):
    return song_json["name"]

def get_song_image(song_json):
    return song_json["album"]["images"][1]['url'] if len(song_json["album"]["images"]) > 1 else song_json["album"]["images"][0]['url']

def get_songs_from_seed(artist_seed, limit=1):
    """Get song recommendations from the Spotify API using an artist_seed"""
    url = "https://api.spotify.com/v1/recommendations"
    query = f"?seed_artists={artist_seed}&limit={limit}"
    headers = get_auth_header(token)
    result = get(url + query, headers=headers)
    
    # Check for rate limiting (429) error
    if result.status_code == 429:
        logger.error("Spotify API rate limit exceeded.")
        return None

    json_result = result.json()
    return json_result.get("tracks", [])

def recommend_seed(song_seed, artist_seed):
    """Generates a list of song recommendations based on seed songs and artists"""
    songs = get_songs_from_seed(artist_seed)
    song_infos = []
    for track in songs:
        song_info = get_song_info(track["id"])
        if song_info == 0:
            continue
        song = Song(song_id=track["id"], name=song_info[1], image=song_info[0],
                    artist=song_info[2], preview=song_info[3], stats=song_info[4], link=song_info[5])
        song_infos.append(song)
    random.shuffle(song_infos)
    return song_infos

def generate_artist_seed(artist_list):
    """Produces a seed usable by the Spotify API based on passed form data"""
    ids = [search_for_artist(token, artist) for artist in artist_list]
    return ",".join(filter(None, ids))

def process_lists(artist_list, stats={}):
    """The main function that returns the recommended songs"""
    token = get_token()
    if not token:
        logger.error("Failed to obtain token")
        return []

    artist_seed = generate_artist_seed(artist_list)
    if not artist_seed:
        logger.error("No valid artists found for seed")
        return []
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
            preview=song_info[3],
            link=song_info[5],
        )
        song_objects.append(song)

    random.shuffle(song_objects)
    return song_objects
