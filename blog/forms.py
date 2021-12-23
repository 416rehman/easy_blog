from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from django.forms import Textarea, TextInput, Select
from tinymce.widgets import TinyMCE
from taggit.forms import TagWidget

from .models import Post, Report


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'excerpt', 'content', 'taglist', 'status', 'featured_image')
        widgets = {
            'excerpt': Textarea(attrs={'aria-label': 'excerpt', 'cols': 20, 'rows': 3, 'oninput': "auto_grow(this)", "onload": "auto_grow(this)",
                                       'onkeypress': 'preventLineBreak(event)', 'placeholder': 'Excerpt', "tabindex": "2"}),
            'title':  Textarea(attrs={'aria-label': 'title', 'cols': 20, 'rows': 4, 'oninput': "auto_grow(this)", "onload": "auto_grow(this)",
                                       'onkeypress': 'preventLineBreak(event)', 'placeholder': 'Title', "tabindex": "1"}),
            'content': TinyMCE(attrs={'aria-label': 'content', "tabindex": "3"}),
            'taglist': TagWidget(attrs={'aria-label': 'tags', 'placeholder': 'Comma-seperated Tags'}),
            'status': Select(attrs={'aria-label': 'status', 'placeholder': 'Status'}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('reason', 'comment')
