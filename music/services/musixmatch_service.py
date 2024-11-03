import requests
import os

BASE_URL = "https://api.musixmatch.com/ws/1.1/"
API_KEY = os.getenv("MUSIXMATCH_API_KEY")

def get_lyrics(artist_name, track_name):
    """
    Fetches lyrics for a given artist and track from Musixmatch API.
    """
    try:
        api_call = f"{BASE_URL}matcher.lyrics.get?format=json&callback=callback&q_artist={artist_name}&q_track={track_name}&apikey={API_KEY}"
        
        response = requests.get(api_call)
        data = response.json()
        
        lyrics = data['message']['body']['lyrics']['lyrics_body']
        
        return lyrics.strip()
    
    except Exception as e:
        return f"An error occurred: {e}"
