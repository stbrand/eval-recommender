from django import forms
from django.forms import formset_factory

from recommender.models import *


RATING_CHOICES =(
    ("0.5", "1"),
    ("1", "2"),
    ("1.5", "3"),
    ("2", "4"),
    ("2.5", "5"),
    ("3", "6"),
    ("3.5", "7"),
    ("4", "8"),
    ("4.5", "9"),
    ("5", "10"),
)


RATING_CHOICES_FULL =(
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
)


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = [
            'user',
            'item',
            'rating'
        ]

class RatingHdForm(forms.Form):
    rating = forms.ChoiceField(choices=RATING_CHOICES)

RatingHdFormSet = formset_factory(RatingHdForm)


class EvaluationForm(forms.ModelForm):
    utility = forms.ChoiceField(choices=RATING_CHOICES_FULL, widget=forms.RadioSelect)
    serendipity = forms.ChoiceField(choices=RATING_CHOICES_FULL, widget=forms.RadioSelect)
    novelty = forms.ChoiceField(choices=RATING_CHOICES_FULL, widget=forms.RadioSelect)
    diversity = forms.ChoiceField(choices=RATING_CHOICES_FULL, widget=forms.RadioSelect)
    unexpectedness = forms.ChoiceField(choices=RATING_CHOICES_FULL, widget=forms.RadioSelect)
    class Meta:
        model = Evaluation
        fields = [
        	'utility',
        	'serendipity',
        	'novelty',
        	'diversity',
        	'unexpectedness',
        ]
