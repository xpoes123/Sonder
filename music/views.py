import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import RecommendationForm, CreateUserForm
from .models import Song
from .services.spotify_service import process_lists
from .services.generative_ai_service import get_dating_profile, parse_dating_profile
import logging

# Configure logging
logger = logging.getLogger(__name__)
User = get_user_model()

def home(request):
    return render(request, 'music/home.html', {})

@login_required
def artist_seed(request):
    form = RecommendationForm()
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            # Collect artist names from the form
            artists = [form.cleaned_data[f'artist_{i}'].strip() for i in range(1, 6) if form.cleaned_data.get(f'artist_{i}')]
            if not artists:
                messages.error(request, "Please enter at least one artist.")
                return redirect('music:artist_seed')
            # Store the artists in the session
            request.session['seed_artists'] = artists
            print(artists)
            print(request.session.get('seed_artists'))
            return redirect('music:recommend')  # Redirect to recommend view after setting seed artists
        else:
            messages.error(request, "Invalid form submission.")
    return render(request, 'music/artist_seed.html', {'form': form})


@login_required
def recommend(request):
    # Fetch seed artists from session
    seed_artists = request.session.get('seed_artists')
    if not seed_artists:
        messages.error(request, "No seed artists found. Please provide artists to get recommendations.")
        return redirect('music:artist_seed')

    # Handle "like" and "dislike" actions
    action = request.GET.get('action')
    spotify_id = request.GET.get('song_id')
    if action and spotify_id:
        # Get or create related liked and disliked song lists for the user
        user = request.user
        song = get_object_or_404(Song, spotify_id=spotify_id)

        if action == 'like':
            # Add to liked songs if not already present
            if not user.liked_songs.filter(id=song.id).exists():
                user.liked_songs.add(song)
                messages.success(request, "You have liked the song.")
                
                # Remove from disliked songs if it exists there
                if user.disliked_songs.filter(id=song.id).exists():
                    user.disliked_songs.remove(song)
                    messages.info(request, "This song was previously disliked; it's now removed from dislikes.")
                
        elif action == 'dislike':
            # Add to disliked songs if not already present
            if not user.disliked_songs.filter(id=song.id).exists():
                user.disliked_songs.add(song)
                messages.success(request, "You have disliked the song.")
                
                # Remove from liked songs if it exists there
                if user.liked_songs.filter(id=song.id).exists():
                    user.liked_songs.remove(song)
                    messages.info(request, "This song was previously liked; it's now removed from likes.")

        return redirect('music:recommend')

    # Generate recommendations without modifying liked_songs
    song_objects = []
    for _ in range(50):
        recommended_songs = process_lists(seed_artists)
        if recommended_songs:
            break
        print(f"Attempt {_}")
        time.sleep(0.25)
    if recommended_songs:
        for song_data in recommended_songs:
            # Retrieve or create song by spotify_id for displaying recommendations only
            song, created = Song.objects.get_or_create(
                spotify_id=song_data.song_id,
                defaults={
                    'name': song_data.name,
                    'artist': song_data.artist[0] if song_data.artist else '',
                    'acoustic': song_data.stats[0],
                    'dance': song_data.stats[1],
                    'duration': song_data.stats[2],
                    'energy': song_data.stats[3],
                    'instrumental': song_data.stats[4],
                    'key': song_data.stats[5],
                    'liveness': song_data.stats[6],
                    'loud': song_data.stats[7],
                    'mode': song_data.stats[8],
                    'speech': song_data.stats[9],
                    'tempo': song_data.stats[10],
                    'valence': song_data.stats[11],
                    'popularity': song_data.stats[12],
                    'image': song_data.image,
                    'preview': song_data.preview,
                    'link': song_data.link,
                }
            )
            # Generate and save dating profile if newly created or profile is missing
            if created or not song.dating_profile:
                dating_profile_text = get_dating_profile(song.name, song_data.artist[0], song_data.stats)
                profile_data = parse_dating_profile(dating_profile_text)
                song.dating_profile = profile_data
                song.save()
            song_objects.append(song)

    context = {
        'recommendations': song_objects,
        'seed_artists': seed_artists,
    }
    return render(request, 'music/recommendations.html', context)



def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account was created for {user.username}")
            return redirect('music:login')
    context = {'form': form}
    return render(request, 'music/register.html', context)

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('music:home')
        else:
            messages.info(request, "Username or Password is incorrect")
    context = {}
    return render(request, 'music/login.html', context)

def logout_user(request):
    logout(request)
    return redirect('music:login')

# music/views.py

def profile(request, user_id):
    # Retrieve the user object using the user ID
    user = get_object_or_404(User, id=user_id)
    # Pass the user object to the template for rendering
    return render(request, 'music/profile.html', {'profile_user': user})
