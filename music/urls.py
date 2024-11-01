# music/urls.py

from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.home, name='home'),
    path('recommend/', views.recommend, name='recommend'),
    path('register/', views.register, name = "register"),
    path('login/', views.login_page, name = "login"),
]
