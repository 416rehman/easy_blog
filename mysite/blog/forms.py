from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from django.forms import Textarea, TextInput, Select
from tinymce.widgets import TinyMCE
from taggit.forms import TagWidget

from .models import Post, Profile, Report


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')


class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].disabled = True


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bio', 'github', 'linkedin', 'website')
        widgets = {
            'avatar': forms.FileInput(attrs={'aria-label': 'Avatar'}),
            'bio': Textarea(attrs={'aria-label': 'bio', 'cols': 20, 'rows': 4, 'oninput': "auto_grow(this)",
                                       'onkeypress': 'preventLineBreak(event)', 'placeholder': 'Bio'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'excerpt', 'content', 'taglist', 'status')
        widgets = {
            'excerpt': Textarea(attrs={'aria-label': 'excerpt', 'cols': 20, 'rows': 2, 'oninput': "auto_grow(this)",
                                       'onkeypress': 'preventLineBreak(event)', 'placeholder': 'Excerpt'}),
            'title': TextInput(
                attrs={'aria-label': 'title', 'onkeypress': 'preventLineBreak(event)', 'placeholder': 'Title'}),
            'content': TinyMCE(attrs={'aria-label': 'content'}),
            'taglist': TagWidget(attrs={'aria-label': 'tags', 'placeholder': 'Comma-seperated Tags'}),
            'status': Select(attrs={'aria-label': 'status', 'placeholder': 'Status'})
        }


class ReportArticleForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('article', 'reason', 'comment', 'reporter')