# music/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RecommendationForm
from .services.spotify_service import process_lists, Song
from .services.generative_ai_service import get_dating_profile, parse_dating_profile
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import logging

# Configure logging
logger = logging.getLogger(__name__)

def home(request):
    form = RecommendationForm()
    # Optionally clear seed_artists when accessing home
    if 'seed_artists' in request.session:
        del request.session['seed_artists']
    return render(request, 'music/home.html', {'form': form})

def recommend(request):
    if request.method == 'POST':
        # Initial recommendation based on user input
        form = RecommendationForm(request.POST)
        if form.is_valid():
            # Collect all artist inputs
            artists = []
            for i in range(1, 6):
                artist = form.cleaned_data.get(f'artist_{i}')
                if artist:
                    artists.append(artist.strip())
            
            # Check if at least one artist is provided
            if not artists:
                messages.error(request, "Please enter at least one artist.")
                return redirect('music:home')
            
            try:
                # Initialize the seed artists in the session
                seed_artists = artists.copy()
                request.session['seed_artists'] = seed_artists

                # Process the seed artists to get Song objects
                for _ in range(20):
                    song_objects = process_lists(seed_artists)
                    if len(song_objects) == 1:
                        break
                else:
                    messages.info(request, "No recommendations found based on your seed artists.")
                    return redirect('music:home')

                # Generate dating profiles for each song
                for song in song_objects:
                    dating_profile_text = get_dating_profile(song.name, song.artist[0], song.stats)
                    profile_data = parse_dating_profile(dating_profile_text)
                    song.dating_profile = profile_data  # Attach profile data to the song object

                context = {
                    'recommendations': song_objects,
                    'seed_artists': seed_artists,  # Ensure seed_artists is passed to the template
                }
                logger.info(f"Generated {len(song_objects)} song recommendations.")
                return render(request, 'music/recommendations.html', context)

            except Exception as e:
                logger.error(f"Error in recommend view (POST): {e}")
                messages.error(request, f"An error occurred while processing your request: {e}")
                return redirect('music:home')
        else:
            # If form is invalid, redirect back to home with errors
            messages.error(request, "Invalid form submission.")
            return redirect('music:home')
    else:
        # Handle GET request, possibly for additional recommendations
        seed_artists = request.session.get('seed_artists', [])
        if not seed_artists:
            messages.error(request, "No seed artists found. Please provide artists to get recommendations.")
            return redirect('music:home')

        try:
            # Process the current seed artists to get Song objects
            for _ in range(20):
                song_objects = process_lists(seed_artists)
                if len(song_objects) == 1:
                    break
            else:
                messages.info(request, "No recommendations found based on your seed artists.")
                return redirect('music:home')

            # Generate dating profiles for each song
            for song in song_objects:
                dating_profile_text = get_dating_profile(song.name, song.artist[0], song.stats)
                profile_data = parse_dating_profile(dating_profile_text)
                song.dating_profile = profile_data  # Attach profile data to the song object

            context = {
                'recommendations': song_objects,
                'seed_artists': seed_artists,  # Ensure seed_artists is passed to the template
            }
            logger.info(f"Generated {len(song_objects)} song recommendations using seed artists.")
            return render(request, 'music/recommendations.html', context)

        except Exception as e:
            logger.error(f"Error in recommend view (GET): {e}")
            messages.error(request, f"An error occurred while processing your request: {e}")
            return redirect('music:home')
