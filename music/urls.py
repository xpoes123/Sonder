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
]
