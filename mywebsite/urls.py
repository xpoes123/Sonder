# mywebsite/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('music.urls')),  # Include music app URLs
    path('accounts/', include('django.contrib.auth.urls')),  # Include Django's auth URLs
]
