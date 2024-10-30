# music/forms.py

from django import forms

class RecommendationForm(forms.Form):
    artists = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter up to 5 artists, separated by commas'}),
        required=False,
        label='Favorite Artists'
    )
