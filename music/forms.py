# forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class RecommendationForm(forms.Form):
    artist_1 = forms.CharField(
        label='Artist 1',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter artist name'})
    )
    artist_2 = forms.CharField(
        label='Artist 2',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter artist name'})
    )
    artist_3 = forms.CharField(
        label='Artist 3',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter artist name'})
    )
    artist_4 = forms.CharField(
        label='Artist 4',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter artist name'})
    )
    artist_5 = forms.CharField(
        label='Artist 5',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter artist name'})
    )
