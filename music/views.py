import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RecommendationForm, CreateUserForm
from .models import Song
from .services.spotify_service import process_lists
from .services.generative_ai_service import get_dating_profile, parse_dating_profile
import logging

# Configure logging
logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'music/home.html', {})

# views.py

def artist_seed(request):
    form = RecommendationForm()
    if 'seed_artists' in request.session:
        del request.session['seed_artists']
    
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            artists = [form.cleaned_data[f'artist_{i}'].strip() for i in range(1, 6) if form.cleaned_data.get(f'artist_{i}')]
            if not artists:
                messages.error(request, "Please enter at least one artist.")
                return redirect('music:artist_seed')
            request.session['seed_artists'] = artists
            return redirect('music:recommend')
        else:
            messages.error(request, "Invalid form submission.")
            return redirect('music:artist_seed')
    
    return render(request, 'music/artist_seed.html', {'form': form})


def recommend(request):
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            artists = [form.cleaned_data[f'artist_{i}'].strip() for i in range(1, 6) if form.cleaned_data.get(f'artist_{i}')]
            if not artists:
                messages.error(request, "Please enter at least one artist.")
                return redirect('music:home')
            try:
                seed_artists = artists.copy()
                request.session['seed_artists'] = seed_artists
                song_objects = []
                for _ in range(20):
                    recommended_songs = process_lists(seed_artists)
                    if recommended_songs:
                        for song_data in recommended_songs:
                            # Check if song is already in the database
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

                        break
                    time.sleep(0.25)
                else:
                    messages.info(request, "No recommendations found based on your seed artists.")
                    return redirect('music:home')

                context = {
                    'recommendations': song_objects,
                    'seed_artists': seed_artists,
                }
                logger.info(f"Generated {len(song_objects)} song recommendations.")
                return render(request, 'music/recommendations.html', context)

            except Exception as e:
                logger.error(f"Error in recommend view (POST): {e}")
                messages.error(request, f"An error occurred while processing your request: {e}")
                return redirect('music:home')
        else:
            messages.error(request, "Invalid form submission.")
            return redirect('music:home')

    else:
        seed_artists = request.session.get('seed_artists', [])
        
        if not seed_artists:
            messages.error(request, "No seed artists found. Please provide artists to get recommendations.")
            return redirect('music:home')

        try:
            song_objects = []
            for _ in range(20):
                recommended_songs = process_lists(seed_artists)
                if recommended_songs:
                    for song_data in recommended_songs:
                        # Check if song is already in the database
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
                    break
                time.sleep(0.25)
                print(f"Attempt {_} failed, trying again")
            else:
                messages.info(request, "No recommendations found based on your seed artists.")
                return redirect('music:home')

            context = {
                'recommendations': song_objects,
                'seed_artists': seed_artists,
            }
            logger.info(f"Generated {len(song_objects)} song recommendations using seed artists.")
            return render(request, 'music/recommendations.html', context)

        except Exception as e:
            logger.error(f"Error in recommend view (GET): {e}")
            messages.error(request, f"An error occurred while processing your request: {e}")
            return redirect('music:home')


def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Account was created for {form.cleaned_data.get('username')}")
            return redirect('music:login')
    context = {'form':form}
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
            messages.info(request, "Username OR Password is incorrect")
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
