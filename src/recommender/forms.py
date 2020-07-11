from django import forms
from django.forms import formset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User as Django_User
from .models import *

import os


DELIMITER_CHOICES = (
    (",", "comma"),
    ("\t", "tab"),
    (" ", "space"),
    ("|", "pipe: |"),
    (";", "semicolon: ;"),
    (":", "colon: :"),
)

SKIP_CHOICES = (
    ("0", "0"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
)

LENGTH_CHOICES = (
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
    ("9", "9"),
    ("10", "10"),
)


class UserLoginForm(forms.Form):
    token = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Input your token here'}))
    class Meta:
        model = User
        fields = [
            'token'
        ]

class UserFilterForm(forms.ModelForm):
    user_id = forms.ModelChoiceField(queryset=User.objects.all().order_by('id'))
    class Meta:
        model = User
        fields = [
            'user_id',
        ]

    def __init__(self,*args,**kwargs):
        dataset = kwargs.pop('dataset')
        print(dataset)
        super().__init__(*args,**kwargs)
        self.fields['user_id'].queryset = User.objects.filter(dataset=dataset)


class UserCreateForm(forms.ModelForm):
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all())
    number = forms.IntegerField()
    class Meta:
        model = Dataset
        fields = [
            'dataset',
            'number'
        ]

class ItemCreateForm(forms.ModelForm):
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.filter(id=81))
    name = forms.CharField()
    poster = forms.ImageField()
    class Meta:
        model = Item
        fields = [
            'dataset',
            'name',
            'poster'
        ]

class FilePathForm(forms.Form):
    path_for_rating_file = forms.FilePathField(label='Path of dataset file with ratings', path = os.path.expanduser('~/.surprise_data/'), recursive=True)
    line_format = forms.CharField(label='Order of entries in each line', widget=forms.TextInput(attrs={'placeholder':'e.g.: user item rating timestamp','size':50}), max_length=255)
    delimiter = forms.ChoiceField(label='Delimiter between entries', choices=DELIMITER_CHOICES)
    skip_lines = forms.ChoiceField(label='Skip lines, where are e.g. headers', choices=SKIP_CHOICES,initial='0')


class AlgorithmForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Input your name here'}))
    class Meta:
        model = Algorithm
        fields = [
            'name',
            'description'
        ]

class AlgorithmFilterForm(forms.ModelForm):
    algorithm = forms.ModelChoiceField(queryset=Algorithm.objects.all().order_by('name'))
    class Meta:
        model = Algorithm
        fields = [
            'algorithm'
        ]

class AlgorithmMultiForm(forms.ModelForm):
    algorithm = forms.ModelMultipleChoiceField(queryset=Algorithm.objects.all().order_by('name'), widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Algorithm
        fields = [
            'algorithm',
        ]

class LengthMultiForm(forms.Form):
    length = forms.MultipleChoiceField(choices=LENGTH_CHOICES, widget=forms.CheckboxSelectMultiple)


class StudyForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Input name here'}))
    algorithms = forms.ModelMultipleChoiceField(queryset=Algorithm.objects.all().order_by('id'), widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = Study
        fields = [
            'name',
            'dataset',
            'algorithms',
            'reclist_length',
            'active',
            'description',
        ]

class StudyFilterForm(forms.ModelForm):
    study = forms.ModelChoiceField(queryset=Study.objects.all().order_by('id'))
    class Meta:
        model = Study
        fields = [
            'study'
        ]


class TokenForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Input token here'}))
    class Meta:
        model = Token
        fields = [
            'name',
        ]

class GenreForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Input title here'}))
    class Meta:
        model = MovieGenre
        fields = [
            'title'
        ]


class DatasetForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Input name here'}))
    class Meta:
        model = Dataset
        fields = [
            'name',
            'size',
            'category',
            'description'
        ]


class DatasetFilterForm(forms.ModelForm):
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all().order_by('id'))
    class Meta:
        model = Dataset
        fields = [
            'dataset'
        ]

class DatasetUserForm(forms.ModelForm):
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.all().order_by('id'))
    user_id = forms.ModelChoiceField(queryset=User.objects.all().order_by('id'))
    class Meta:
        model = User
        fields = [
            'dataset',
            'user_id'
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_id'].queryset = User.objects.none()

        if 'dataset' in self.data:
            try:
                dataset = self.data.get('dataset')
                self.fields['user_id'].queryset = User.objects.filter(dataset=dataset).order_by('user_id')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty user queryset
        elif self.instance.pk:
            self.fields['user_id'].queryset = User.objects.none()
