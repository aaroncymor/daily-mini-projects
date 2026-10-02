from django import forms
from .models import MEDIA_TYPE_CHOICES


class SearchForm(forms.Form):
    title = forms.CharField(label="Search by title...")


class BacklogItemForm(forms.Form):
    id = forms.IntegerField()
    title = forms.CharField(label="Anime / Manga title")
    mal_id = forms.CharField(label="MyAnimeList ID")
    media_type = forms.ChoiceField(choices=MEDIA_TYPE_CHOICES)
    current_progress = forms.IntegerField()
    total_units = forms.IntegerField()
    start_date = forms.DateField()
    target_date = forms.DateField()
