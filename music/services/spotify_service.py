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
    """
    Debugging tool
    """
    print(json.dumps(json_file, indent=4))

def get_token():
    """
    Obtain an OAuth token for the Spotify API.
    """
    auth_string = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    if result.status_code == 200:
        json_result = result.json()
        token = json_result.get("access_token")
        if token:
            return token
        else:
            logger.error("Failed to retrieve access token: %s", json_result)
    else:
        logger.error("Failed to get token, status: %s, response: %s", result.status_code, result.text)
    return None

token = get_token()

def get_auth_header(token):
    """
    Get the spotify header with the provided token
    """
    return {"Authorization": f"Bearer {token}"}

def search_for_artist(token, artist_name):
    """
    Find the artist based on the artist name using the Spotify API
    """
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
    """
    Find similar artists based on other artist using the Spotify API
    Unused method, could be used in the future
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()
    related_artists = json_result.get('artists', [])[:limit]
    return related_artists

def get_artist_tracks(token, artist_id):
    """
    Find the top songs of an artist using the Spotify API
    Unused method, could be used in the future
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = result.json()
    return json_result["tracks"]

def get_track_link(json_result):
    """
    Returns the link of a song, helper method
    """
    return json_result["album"]["external_urls"]["spotify"]

def get_song_info(song_id):
    """
    Returns all of the info of a song using the Spotify API
    """
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
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
    """
    Creates a dating profile for a song
    """
    return gemini.get_dating_profile(song.name, song.artist[0], song.stats)

def get_song_stats(song_id):
    """
    Returns all of the stats of a song using the Spotify API
    """
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

def get_songs_from_seed(artist_seed, limit = 1):
    """
    Get song recommendations from the spotify API using an artist_seed provided by the user
    """
    url = "https://api.spotify.com/v1/recommendations"
    query = ""
    if artist_seed:
        query += f"seed_artists={artist_seed}&limit={limit}"
    url += f"?{query}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    print(result)
    json_result = result.json()
    return json_result.get("tracks", [])

def recommend_seed(song_seed, artist_seed):
    """
    I don't really remember what this was for, I don't think this is being used
    """
    songs = get_songs_from_seed(song_seed, artist_seed)
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
    """
    Produces a seed usable by the Spotify API based on passed form data
    """
    ids = [search_for_artist(token, artist) for artist in artist_list]
    artist_seed = ",".join(filter(None, ids))
    return artist_seed

def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def api_request(url, headers):
    """
    Method to run the json requests
    """
    try:
        result = get(url, headers=headers)
        result.raise_for_status()
        return result.json()
    except Exception as e:
        logger.error("Error making API request to %s: %s", url, e)
        return None

def search_for_artist(token, artist_name):
    """
    Get the ID of an artist for easier use
    """
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    json_result = api_request(query_url, headers)
    if json_result:
        artists = json_result.get("artists", {}).get("items", [])
        if artists:
            return artists[0].get("id")
    logger.warning("No artist found for %s", artist_name)
    return None

def process_lists(artist_list, stats={}):
    """
    The main function that returns the recommended songs
    """
    token = get_token()
    if not token:
        logger.error("Failed to obtain token")
        return []

    artist_seed = generate_artist_seed(artist_list)
    if not artist_seed:
        logger.error("No valid artists found for seed")
        return []
    tracks = get_songs_from_seed(artist_seed, stats)
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