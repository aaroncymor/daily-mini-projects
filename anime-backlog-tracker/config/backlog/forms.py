from django import forms


class SearchForm(forms.Form):
    title = forms.CharField(label="Search by title...")


class BacklogItemForm(forms.Form):
    title = forms.CharField()
