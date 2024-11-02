# Assuming this is in your services or recommendation logic file

# Import necessary models and libraries
from authuser.models import User, UserCluster
from music.models import Song
from sklearn.cluster import KMeans
from django.db import transaction
import numpy as np

def elbow_method(vectors, max_clusters=10, threshold=0.1):
    """
    Find the optimal number of clusters using the elbow method without plotting.

    Parameters:
    - vectors: List of feature vectors to cluster.
    - max_clusters: Maximum number of clusters to consider.
    - threshold: Threshold for the minimum rate of change in inertia.

    Returns:
    - optimal_k: Optimal number of clusters based on the elbow method.
    """
    inertia_values = []
    n_samples = len(vectors)
    
    # Determine the maximum number of clusters to fit based on sample size
    max_clusters = min(max_clusters, n_samples)
    
    # Calculate inertia for each number of clusters
    for k in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(vectors)
        inertia_values.append(kmeans.inertia_)
    
    # Compute the rate of change in inertia values
    rate_of_change = np.diff(inertia_values)
    second_derivative = np.diff(rate_of_change)
    
    # Identify the optimal k by finding where the second derivative becomes stable (near zero)
    optimal_k = 1
    for i, change in enumerate(second_derivative):
        if abs(change) < threshold:
            optimal_k = i + 2  # +2 because we are checking for the 2nd derivative and indexing starts at 0
            break
        
    return optimal_k

def calculate_centroids(vectors):
    """
    Calculate centroids and radii for clusters of vectors.
    
    Parameters:
    - vectors: List of feature vectors to cluster.
    
    Returns:
    - clusters: List of dictionaries with 'centroid' and 'radius' for each cluster.
    """
    optimal_k = elbow_method(vectors)
    kmeans = KMeans(n_clusters=optimal_k)
    kmeans.fit(vectors)
    centroids = kmeans.cluster_centers_
    
    clusters = []
    for i, center in enumerate(centroids):
        cluster_points = np.array(vectors)[np.where(kmeans.labels_ == i)]
        radius = np.max(np.linalg.norm(cluster_points - center, axis=1)) if len(cluster_points) > 0 else 0
        clusters.append({
            "centroid": center.tolist(),  # Convert to list for JSON storage
            "radius": radius
        })
    
    return clusters

def cluster(user):
    """
    Cluster the liked and disliked songs for a user and store the results in UserCluster.
    
    Parameters:
    - user: The User instance to cluster songs for.
    """
    # Access liked songs and normalize features
    liked_songs = user.liked_songs.all()
    liked_vectors = [
        [song.acoustic, song.dance, song.liveness, (song.tempo - 50) / 200, song.valence, song.popularity / 100]
        for song in liked_songs
    ]
    
    # Access disliked songs and normalize features
    disliked_songs = user.disliked_songs.all()
    disliked_vectors = [
        [song.acoustic, song.dance, song.liveness, (song.tempo - 50) / 200, song.valence, song.popularity / 100]
        for song in disliked_songs
    ]
    
    # Calculate clusters for liked and disliked songs if there are enough vectors
    liked_clusters = calculate_centroids(liked_vectors) if len(liked_vectors) > 1 else []
    disliked_clusters = calculate_centroids(disliked_vectors) if len(disliked_vectors) > 1 else []
    
    # Use a transaction to ensure atomicity
    with transaction.atomic():
        user_cluster, created = UserCluster.objects.get_or_create(user=user)
        
        # Update fields regardless of whether a new instance was created or an existing one was retrieved
        user_cluster.liked_clusters = liked_clusters
        user_cluster.disliked_clusters = disliked_clusters
        user_cluster.save()

    print(f"Updated clusters for user {user.username}.")
    print(f"Liked clusters: {liked_clusters}")
    print(f"Disliked clusters: {disliked_clusters}")
