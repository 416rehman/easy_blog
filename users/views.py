from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import UpdateView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from blog.forms import ReportForm
from blog.models import Post
from mysite import settings
from users.forms import UserForm, ProfileForm, SignupForm
from users.tokens import account_activation_token
from blog.serializers import PostSerializer


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(get_user_model(), pk=uid)
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


@login_required
def ReportUserView(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    if user.username == request.user.username:
        return redirect('profile_page', username=username)
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
    following = follows_back = False
    if request.user.username == username:
        user = request.user
        posts = Post.objects.filter(author__username=user.username)
    else:

        user = get_object_or_404(get_user_model(), username=username)
        posts = Post.objects.filter(author__username=user.username, status=1)
        if request.user.is_authenticated:
            following = user.is_followed_by(request.user.username)
            follows_back = request.user.is_followed_by(user.username)

    context = {
        'requested_profile': user,
        'posts': posts,
        'following': following,
        'follows_back': follows_back
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
            # Check that the username is not restricted

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            if form.cleaned_data.get('username') in settings.RESTRICTED_USERNAMES:
                messages.add_message(request, messages.ERROR, 'Username is restricted')
                return redirect('signup')

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
        return get_object_or_404(get_user_model(), pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_email_verified:
                return redirect('home')
            else:
                return super().get(request, *args, **kwargs)
        else:
            return redirect('home')

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, 'An email has been sent. Please check your email.')
        return super().get(request, *args, **kwargs)


@login_required()
def AJAX_FollowUserView(request, username):
    session_user = get_object_or_404(get_user_model(), username=request.user.username)
    other_user = get_object_or_404(get_user_model(), username=username)

    action = "Failed to follow {0}".format(username)
    if session_user.username != other_user.username:
        if other_user.is_followed_by(session_user.username):
            session_user.unfollow(other_user)
            action = 'Unfollowed {0}'.format(other_user.username)
        else:
            session_user.follow(other_user)
            action = 'Followed {0}'.format(other_user.username)

    return JsonResponse({'action': action})


@login_required()
def UserFollowersView(request, username):
    target_user = get_object_or_404(get_user_model(), username=username)
    target_followers = target_user.followers.all()
    page = request.GET.get('p', 1)

    paginator = Paginator(target_followers, 10)
    try:
        followers = paginator.page(page)
    except PageNotAnInteger:
        followers = paginator.page(1)
    except EmptyPage:
        followers = paginator.page(paginator.num_pages)
    return render(request, 'followers.html', {'users': followers, 'target_user': target_user})


@login_required()
def UserFollowingView(request, username):
    target_user = get_object_or_404(get_user_model(), username=username)
    target_following = get_user_model().objects.filter(followers__username=username)
    page = request.GET.get('p', 1)

    paginator = Paginator(target_following, 10)
    try:
        following = paginator.page(page)
    except PageNotAnInteger:
        following = paginator.page(1)
    except EmptyPage:
        following = paginator.page(paginator.num_pages)
    return render(request, 'following.html', {'users': following, 'target_user': target_user})


# create an api to get the user's posts
@api_view(['GET'])
def UserPostsView(request, username):
    posts = Post.objects.filter(author__username=username, status=1).all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)
