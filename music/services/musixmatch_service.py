# music/services/musixmatch_service.py

import requests

# Musixmatch API base URL and API key
BASE_URL = "https://api.musixmatch.com/ws/1.1/"
API_KEY = "159a41f6c1072ba09a7fceeb9d8b2c5a"  # Consider moving this to environment variables

def get_lyrics(artist_name, track_name):
    """
    Fetches lyrics for a given artist and track from Musixmatch API.
    """
    try:
        # Construct the API call
        api_call = f"{BASE_URL}matcher.lyrics.get?format=json&callback=callback&q_artist={artist_name}&q_track={track_name}&apikey={API_KEY}"
        
        # Make the request to the API
        response = requests.get(api_call)
        data = response.json()
        
        # Extract the lyrics from the response
        lyrics = data['message']['body']['lyrics']['lyrics_body']
        
        return lyrics.strip()
    
    except Exception as e:
        return f"An error occurred: {e}"
