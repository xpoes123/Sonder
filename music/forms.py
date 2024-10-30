# music/forms.py

from django import forms

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
