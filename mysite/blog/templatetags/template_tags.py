from django import template
from django.contrib.auth import get_user_model

from mysite import settings

register = template.Library()


@register.inclusion_tag('components/profile-card.html')
def profile_card(request, user=None, minimal=False):
    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'bio': user.profile.bio,
        'avatar': 'https://s3.amazonaws.com/' + settings.AWS_STORAGE_BUCKET_NAME + '/' + settings.AWS_PUBLIC_MEDIA_LOCATION + '/' + str(
            user.profile.avatar),
        'banner': 'https://s3.amazonaws.com/' + settings.AWS_STORAGE_BUCKET_NAME + '/' + settings.AWS_PUBLIC_MEDIA_LOCATION + '/' + str(
            user.profile.banner),
        'following': user.followers.filter(username=request.user.username) if request.user.is_authenticated else False,
        'follows_back': request.user.is_followed_by(user.username) if request.user.is_authenticated else False,
        'follower_count': user.count_followers,
        'following_count': user.count_following,
        'minimal': minimal,
        'request': request
    }


@register.inclusion_tag('components/post-card.html')
def post_card(post):
    return {
        'post': post,
    }

@register.inclusion_tag('components/post-card.html')
def post_card(post):
    return {
        'post': post,
    }
