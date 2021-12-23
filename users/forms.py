from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import Textarea

from blog.models import Profile


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
        fields = ('avatar', 'banner', 'bio', 'github', 'linkedin', 'website')
        widgets = {
            'avatar': forms.FileInput(attrs={'aria-label': 'Avatar'}),
            'banner': forms.FileInput(attrs={'aria-label': 'Banner'}),
            'bio': Textarea(attrs={'aria-label': 'bio', 'cols': 20, 'rows': 6, 'oninput': "auto_grow(this)",
                                   'onkeypress': 'preventLineBreak(event)', 'placeholder': 'Bio'}),
            'github': forms.TextInput(attrs={'aria-label': 'Github URL', 'placeholder': 'https://github.com/...'}),
            'linkedin': forms.TextInput(attrs={'aria-label': 'LinkedIn URL', 'placeholder': 'https://linkedin.com/in/...'}),
            'website': forms.TextInput(attrs={'aria-label': 'Website URL', 'placeholder': 'https://yourwebsite.com/'})
        }


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')


class EmailVerificationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('email',)
