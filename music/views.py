# music/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RecommendationForm
from .services.spotify_service import process_lists, Song
from .services.generative_ai_service import get_dating_profile, parse_dating_profile
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import logging

# Configure logging
logger = logging.getLogger(__name__)

def home(request):
    form = RecommendationForm()
    return render(request, 'music/home.html', {'form': form})

def recommend(request):
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            songs_input = form.cleaned_data.get('songs', '')
            artists_input = form.cleaned_data.get('artists', '')
            
            # Split the inputs into lists, limit to 5
            songs_list = [song.strip() for song in songs_input.split(',') if song.strip()][:5]
            artists_list = [artist.strip() for artist in artists_input.split(',') if artist.strip()][:5]
            
            # Check limits
            if len(songs_input.split(',')) > 5 or len(artists_input.split(',')) > 5:
                messages.warning(request, "You can only add up to 5 songs and 5 artists.")
                return redirect('music:home')
            
            if not songs_list and not artists_list:
                messages.error(request, "Please enter at least one song or artist.")
                return redirect('music:home')
            
            try:
                # Process the lists to get Song objects
                song_objects = process_lists(songs_list, artists_list)
                
                if not song_objects:
                    messages.info(request, "No recommendations found based on your input.")
                    return redirect('music:home')
                
                # Generate dating profiles for each song
                for song in song_objects:
                    dating_profile_text = get_dating_profile(song.name, song.artist[0], song.stats)
                    profile_data = parse_dating_profile(dating_profile_text)
                    song.dating_profile = profile_data  # Attach profile data to the song object
                
                context = {
                    'recommendations': song_objects
                }
                logger.info(f"Generated {len(song_objects)} song recommendations.")
                return render(request, 'music/recommendations.html', context)
            
            except Exception as e:
                logger.error(f"Error in recommend view: {e}")
                messages.error(request, f"An error occurred while processing your request: {e}")
                return redirect('music:home')
    else:
        return redirect('music:home')


@require_POST
# @login_required  # Uncomment if authentication is required
def like(request):
    try:
        # Implement your like processing logic here
        # For example, increment a like count, associate the like with a user, etc.
        # Example:
        # song_id = request.POST.get('song_id')
        # song = Song.objects.get(id=song_id)
        # song.likes += 1
        # song.save()

        logger.info("User liked a song.")
        response = {'status': 'success', 'message': 'You liked the song!'}
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in like view: {e}")
        response = {'status': 'error', 'message': 'An error occurred while liking the song.'}
        return JsonResponse(response, status=500)

