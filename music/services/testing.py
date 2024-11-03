from dotenv import load_dotenv
import os
import base64
from requests import post, get

# Load environment variables from .env file
load_dotenv()

def get_token():
    """
    Obtain an OAuth token for the Spotify API.
    """
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not client_id or not client_secret:
        print("CLIENT_ID or CLIENT_SECRET is missing.")
        return None

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

    if result.status_code != 200:
        print(f"Failed to get token, status code: {result.status_code}, response: {result.text}")
        return None

    json_result = result.json()
    token = json_result.get("access_token")
    print("Access token:", token)
    return token

def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

def search_for_artist(token, artist_name):
    """
    Get the ID of an artist for easier use
    """
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query

    # Make the API request
    result = get(query_url, headers=headers)
    
    # Check if the result is successful
    if result.status_code != 200:
        print(f"Error in API call: {result.status_code} - {result.text}")
        return None

    # Print the full response for debugging
    json_result = result.json()
    print("Full JSON response:", json_result)  # Debug output

    # Check if the response contains the expected data
    artists = json_result.get("artists", {}).get("items", [])
    if not artists:
        print("No artists found in the response.")
        return None

    # Return the artist ID
    artist_id = artists[0].get("id")
    print(f"Artist ID for {artist_name}: {artist_id}")
    return artist_id

# Get the token and test the search
token = get_token()
print(search_for_artist(token, "Phoebe Bridgers"))
