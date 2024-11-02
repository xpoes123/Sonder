# music/urls.py

from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.home, name='home'),
    path('recommend/', views.recommend, name='recommend'),
    path('artist_seed/', views.artist_seed, name='artist_seed'),
    path('register/', views.register, name = "register"),
    path('login/', views.login_page, name = "login"),
    path('logout/', views.logout_user, name = "logout"),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('profile/<int:user_id>/song_list/', views.song_list, name='song_list'),
    path('profile/<int:user_id>/liked_songs/remove/<str:song_id>/', views.remove_liked_song, name='remove_liked_song'),
    path('profile/<int:user_id>/disliked_songs/remove/<str:song_id>/', views.remove_disliked_song, name='remove_disliked_song'),

]
