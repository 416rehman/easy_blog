from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import UpdateView

from blog.forms import ReportForm
from blog.models import Post
from users.forms import UserForm, ProfileForm, SignupForm, EmailVerificationForm
from users.tokens import account_activation_token


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_email_verified = True
            user.save()
            login(request, user)
            messages.success(request, 'Email Confirmed')
            return redirect('home')
        else:
            # invalid link
            messages.error(request, 'Invalid URL')
            return redirect('home')


def ReportUserView(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    if user:
        userReportForm = ReportForm(request.POST or None)

        if userReportForm.is_valid():
            new_report = userReportForm.save(commit=False)
            new_report.user = user
            if request.user:
                new_report.reporter = request.user
            new_report.save()

            messages.add_message(request, messages.SUCCESS, 'User Reported')
            return redirect('profile_page', username=username)

        return render(request, 'report.html', context={'form': userReportForm})


@login_required
def EditProfileView(request, username):
    instance = get_object_or_404(get_user_model(), username=username)

    if instance.username != request.user.username:
        return redirect('profile_page', username=username)

    userForm = UserForm(request.POST or None, instance=instance)
    profileForm = ProfileForm(request.POST or None, instance=instance.profile)
    if request.method == 'POST':
        profileForm = ProfileForm(request.POST or None, request.FILES, instance=instance.profile)

    if userForm.is_valid() and profileForm.is_valid():
        user_instance = userForm.save(commit=False)
        if 'email' in userForm.changed_data:
            user_instance.is_email_verified = False
            messages.add_message(request, messages.INFO, 'Verify your new email')
        user_instance.save()

        profileForm.save()
        messages.add_message(request, messages.SUCCESS, 'Profile updated!')
        return redirect('profile_page', username=username)
    context = {
        'userForm': userForm,
        'profileForm': profileForm
    }
    return render(request, 'edit_profile.html', context=context)


def ProfileView(request, username):
    if request.user.username == username:
        user = request.user
        posts = Post.objects.filter(author=user)
    else:
        user = get_user_model().objects.get(username=username)
        posts = Post.objects.filter(author=user, status=1)

    context = {
        'requested_profile': user,
        'posts': posts
    }
    return render(request, 'profile.html', context=context)


def SignUpView(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'GET':
        form = SignupForm
        return render(request, 'registration/signup.html', {'form': form})

    else:
        form = SignupForm(request.POST or None)
        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.add_message(request, messages.SUCCESS, 'Welcome to Easy Blog!')
            messages.add_message(request, messages.SUCCESS, 'Check your email to finish signing up.')

            return redirect('home')
        else:
            for e in form.errors:
                messages.add_message(request, messages.ERROR, e)
            return render(request, 'registration/signup.html', {'form': form, 'newPost': True})


class InactiveUserView(UpdateView):
    model = get_user_model()
    fields = ['email']
    template_name = 'registration/activate.html'
    success_url = '/activate'

    def get_object(self, **kwargs):
        return get_user_model().objects.get(pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_email_verified:
            return redirect('home')
        else:
            return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, 'An email has been sent. Please check your email.')
        return super().get(request, *args, **kwargs)
