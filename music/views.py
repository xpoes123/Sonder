import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import RecommendationForm, CreateUserForm
from .models import Song, Cluster
from .services.spotify_service import process_lists
from .services.generative_ai_service import get_dating_profile, parse_dating_profile, get_phrase_from_cluster
from .services.clustering_service import cluster
import logging
import numpy as np
import random

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
            return redirect('music:recommend')  # Redirect to recommend view after setting seed artists
        else:
            messages.error(request, "Invalid form submission.")
    return render(request, 'music/artist_seed.html', {'form': form})


@login_required
def recommend(request):
    # Fetch seed artists from session
    seed_artists = request.session.get('seed_artists')
    user = request.user
    if not seed_artists:
        messages.error(request, "No seed artists found. Please provide artists to get recommendations.")
        return redirect('music:artist_seed')

    # Handle "like" and "dislike" actions
    action = request.GET.get('action')
    spotify_id = request.GET.get('song_id')
    if action and spotify_id:
        user = request.user
        song = get_object_or_404(Song, spotify_id=spotify_id)
        
        # Run clustering if needed
        print(user.get_song_count())
        if user.get_song_count() % 5 == 0:
            print("Clustering")
            cluster(user)
        
        if action == 'like':
            if not user.liked_songs.filter(id=song.id).exists():
                user.liked_songs.add(song)
                user.increment_liked_song_count()
                messages.success(request, "You have liked the song.")
                
                if user.disliked_songs.filter(id=song.id).exists():
                    user.disliked_songs.remove(song)
                    messages.info(request, "This song was previously disliked; it's now removed from dislikes.")
        elif action == 'dislike':
            if not user.disliked_songs.filter(id=song.id).exists():
                user.disliked_songs.add(song)
                user.increment_disliked_song_count()
                messages.success(request, "You have disliked the song.")
                
                if user.liked_songs.filter(id=song.id).exists():
                    user.liked_songs.remove(song)
                    messages.info(request, "This song was previously liked; it's now removed from likes.")

        return redirect('music:recommend')

    # Retrieve user's clusters if they have rated more than 25 songs
    liked_clusters = []
    disliked_clusters = []
    if user.get_song_count() > 25:
        user_clusters = user.user_cluster  # Assuming one UserCluster instance per user with liked and disliked clusters
        liked_clusters = user_clusters.liked_clusters
        disliked_clusters = user_clusters.disliked_clusters

    # Generate recommendations
    song_objects = []
    for _ in range(50):
        recommended_songs = process_lists(seed_artists)
        if recommended_songs:
            for song_data in recommended_songs:
                song_vector = [
                    song_data.stats[0],  # acousticness
                    song_data.stats[1],  # danceability
                    song_data.stats[6],  # liveness
                    (song_data.stats[10] - 50) / 200,  # tempo normalized
                    song_data.stats[11],  # valence
                    song_data.stats[12] / 100  # popularity normalized
                ]
                
                # Check if the song vector is in a liked cluster and not in a disliked cluster
                if user.get_song_count() > 25:
                    if random.randint(0,100) < 60 and (not is_in_disliked_clusters(song_vector, disliked_clusters) and is_in_liked_clusters(song_vector, liked_clusters)):
                        song_objects.append(create_or_update_song(song_data))
                        context = {
                            'recommendations': song_objects,
                            'seed_artists': seed_artists,
                        }
                        print("Recommended")
                        return render(request, 'music/recommendations.html', context)
                    elif random.randint(0,100) < 60:
                        song_objects.append(create_or_update_song(song_data))
                        context = {
                            'recommendations': song_objects,
                            'seed_artists': seed_artists,
                        }
                        print("Fake Recommended")
                        return render(request, 'music/recommendations.html', context)
                    else:
                        print(f"Song not in recommendation")
                        continue
                else:
                    print(user.get_song_count())
                    song_objects.append(create_or_update_song(song_data))
                    context = {
                        'recommendations': song_objects,
                        'seed_artists': seed_artists,
                    }
                    print("Not recommended")
                    return render(request, 'music/recommendations.html', context)
        else:
            print(f"Attempt {_}")
            time.sleep(1)

    context = {
        'recommendations': song_objects,
        'seed_artists': seed_artists,
    }
    return render(request, 'music/recommendations.html', context)

def is_in_liked_clusters(song_vector, liked_clusters):
    """Checks if a song vector is within any of the disliked clusters."""
    song_vector = np.array(song_vector, dtype=float)  # Ensure song_vector is numeric

    for entry in liked_clusters:
        # Convert the centroid to a numpy array and compute the distance
        centroid = np.array(entry['centroid'], dtype=float)
        distance = np.linalg.norm(song_vector - centroid)
        
        # Check if the distance is within the specified radius
        if distance <= entry['radius']:
            return True
    return False


def is_in_disliked_clusters(song_vector, disliked_clusters):
    """Checks if a song vector is within any of the disliked clusters."""
    song_vector = np.array(song_vector, dtype=float)  # Ensure song_vector is numeric

    for entry in disliked_clusters:
        # Convert the centroid to a numpy array and compute the distance
        centroid = np.array(entry['centroid'], dtype=float)
        distance = np.linalg.norm(song_vector - centroid)
        
        # Check if the distance is within the specified radius
        if distance <= entry['radius']:
            return True
    return False



def create_or_update_song(song_data):
    """Creates or updates a song based on the song_data from Spotify."""
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
    if created or not song.dating_profile:
        dating_profile_text = get_dating_profile(song.name, song_data.artist[0], song_data.stats)
        profile_data = parse_dating_profile(dating_profile_text)
        song.dating_profile = profile_data
        song.save()
    return song

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

def profile(request, user_id):
    # Retrieve the user object using the user ID
    user = get_object_or_404(User, id=user_id)
    # Pass the user object to the template for rendering
    return render(request, 'music/profile.html', {'profile_user': user})

def song_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    liked_songs = [
        {
            'image': song.image,
            'title': song.name,
            'artist': song.artist,
            'acousticness': round(song.acoustic, 2),
            'danceability': round(song.dance, 2),
            'liveness': round(song.liveness, 2),
            'tempo': round((song.tempo - 50) / 200, 2),
            'valence': round(song.valence, 2),
            'popularity': round(song.popularity / 100, 2) if song.popularity is not None else 0,
            'spotify_id': song.spotify_id
        }
        for song in user.liked_songs.all()
    ]

    disliked_songs = [
        {
            'image': song.image,
            'title': song.name,
            'artist': song.artist,
            'acousticness': round(song.acoustic, 2),
            'danceability': round(song.dance, 2),
            'liveness': round(song.liveness, 2),
            'tempo': round((song.tempo - 50) / 200, 2),
            'valence': round(song.valence, 2),
            'popularity': round(song.popularity / 100, 2) if song.popularity is not None else 0,
            'spotify_id': song.spotify_id
        }
        for song in user.disliked_songs.all()
    ]
    
    # Check if the view should start with disliked songs displayed
    initial_view = request.GET.get('view', 'liked')  # Defaults to 'liked' if no parameter is present
    
    return render(request, 'music/song_list.html', {
        'profile_user': user,
        'liked_songs': liked_songs,
        'disliked_songs': disliked_songs,
        'initial_view': initial_view
    })

def remove_liked_song(request, user_id, song_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        song = get_object_or_404(Song, spotify_id=song_id)
        user.liked_songs.remove(song)  # Assuming a ManyToMany relationship
        messages.success(request, f"{song.name} was removed from your liked songs.")
    return redirect('music:liked_songs', user_id=user_id)


def remove_disliked_song(request, user_id, song_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        song = get_object_or_404(Song, spotify_id=song_id)
        user.disliked_songs.remove(song)
        messages.success(request, f"{song.name} was removed from your disliked songs.")
    return redirect(f'/profile/{user_id}/liked_songs/?view=disliked')

def get_user_cluster(centroid):
    """Creates or retrieves a cluster for the user with a classified name."""
    
    # Define the classification scheme
    classification_scheme = {
        "acousticness": ["Synthetic", "Mild", "Organic", "Pure"],
        "danceability": ["Dead", "Stiff", "Groovy", "Danceable"],
        "liveness": ["Studio", "Muted", "Lively", "Live"],
        "tempo": ["Slow", "Mellow", "Upbeat", "Fast"],
        "valence": ["Gloomy", "Neutral", "Happy", "Joyful"],
        "popularity": ["Niche", "Hidden", "Known", "Basic"],
    }

    def classify_value(attribute, value):
        """Classify a numeric attribute into one of four categories."""
        ranges = [0.25, 0.5, 0.75, 1.0]
        for i, threshold in enumerate(ranges):
            if value < threshold:
                return classification_scheme[attribute][i]
        return classification_scheme[attribute][-1]  # Default to last category

    # Generate classification name based on centroid values
    attributes = ["acousticness", "danceability", "liveness", "tempo", "valence", "popularity"]
    classification_name = "-".join(
        classify_value(attr, centroid[idx]) for idx, attr in enumerate(attributes)
    )

    # Check if a cluster with the same classification name exists
    existing_cluster = Cluster.objects.filter(name=classification_name).first()

    if existing_cluster:
        return existing_cluster.genre  # Return existing cluster if found

    # If no existing cluster, create a new one with a generated name
    name = get_phrase_from_cluster(classification_name)
    cluster = Cluster(name=classification_name, genre=name)
    cluster.save()
    return cluster.genre

def is_song_in_cluster(song, centroid, radius=0.15):  # Increased tolerance for testing
    """
    Determines if a song belongs to a cluster based on a tolerance.
    Adjust the tolerance to make clustering more or less strict.
    """
    # Create song vector with normalized values and rounding for consistency
    song_vector = [
        round(song.acoustic, 2),
        round(song.dance, 2),
        round(song.liveness, 2),
        round((song.tempo - 50) / 200, 2),
        round(song.valence, 2),
        round(song.popularity / 100 if song.popularity is not None else 0, 2)
    ]
    
    # Calculate distance between the song vector and the cluster centroid
    distance = np.linalg.norm(np.array(song_vector) - np.array(centroid))
    
    # Debugging output to check values and distance
    # print(f"Checking song '{song.name}' with vector {song_vector} against centroid {centroid}")
    # print(f"Distance: {distance}, Tolerance: {radius}")
    
    return distance <= radius

def user_cluster_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_cluster = user.user_cluster  # Assuming a one-to-one relationship with UserCluster

    # Retrieve liked and disliked clusters from JSON fields
    liked_clusters = user_cluster.liked_clusters or []
    disliked_clusters = user_cluster.disliked_clusters or []

    liked_cluster_instances = []
    for cluster in liked_clusters:
        # Get cluster name and rounded centroid
        cluster_name = get_user_cluster(cluster['centroid'])
        rounded_centroid = [round(val, 2) for val in cluster['centroid']]
        radius = cluster['radius']
        
        # Find songs in the user's liked songs that belong to this cluster
        cluster_songs = []
        for song in user.liked_songs.all():
            if is_song_in_cluster(song, rounded_centroid, radius):  # Pass rounded centroid
                cluster_songs.append({
                    "image": song.image,
                    "title": song.name,
                    "artist": song.artist,
                    "acousticness": round(song.acoustic, 2),
                    "danceability": round(song.dance, 2),
                    "liveness": round(song.liveness, 2),
                    "tempo": round((song.tempo - 50) / 200, 2),
                    "valence": round(song.valence, 2),
                    "popularity": round(song.popularity / 100, 2) if song.popularity is not None else 0
                })
        
        # Append each cluster with its name, centroid, and associated songs
        liked_cluster_instances.append({
            "name": cluster_name,
            "centroid": rounded_centroid,
            "songs": cluster_songs
        })
    
    disliked_cluster_instances = []
    for cluster in disliked_clusters:
        # Get cluster name and rounded centroid
        cluster_name = get_user_cluster(cluster['centroid'])
        rounded_centroid = [round(val, 2) for val in cluster['centroid']]
        radius = cluster['radius']
        
        # Find songs in the user's liked songs that belong to this cluster
        cluster_songs = []
        for song in user.disliked_songs.all():
            if is_song_in_cluster(song, rounded_centroid, radius):  # Pass rounded centroid
                cluster_songs.append({
                    "image": song.image,
                    "title": song.name,
                    "artist": song.artist,
                    "acousticness": round(song.acoustic, 2),
                    "danceability": round(song.dance, 2),
                    "liveness": round(song.liveness, 2),
                    "tempo": round((song.tempo - 50) / 200, 2),
                    "valence": round(song.valence, 2),
                    "popularity": round(song.popularity / 100, 2) if song.popularity is not None else 0
                })
        
        # Append each cluster with its name, centroid, and associated songs
        disliked_cluster_instances.append({
            "name": cluster_name,
            "centroid": rounded_centroid,
            "songs": cluster_songs
        })

    context = {
        "profile_user": user,
        "liked_clusters": liked_cluster_instances,
        "disliked_clusters": disliked_cluster_instances
    }
    return render(request, "music/user_clusters.html", context)