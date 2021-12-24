from datetime import datetime

from django import template
from django.contrib.auth import get_user_model
from django.template import defaultfilters

from mysite import settings

register = template.Library()


@register.inclusion_tag('components/profile-card.html')
def profile_card(request, user=None, minimal=False, model_object=True):
    print(user)
    if model_object:
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'bio': user.profile.bio,
            'avatar': 'http://s3.amazonaws.com/' + settings.AWS_STORAGE_BUCKET_NAME + '/' + settings.AWS_PUBLIC_MEDIA_LOCATION + '/' + str(
                user.profile.avatar),
            'banner': 'http://s3.amazonaws.com/' + settings.AWS_STORAGE_BUCKET_NAME + '/' + settings.AWS_PUBLIC_MEDIA_LOCATION + '/' + str(
                user.profile.banner),
            'following': user.followers.filter(username=request.user.username).exists() if request.user.is_authenticated else False,
            'follows_back': request.user.is_followed_by(user.username) if request.user.is_authenticated else False,
            'follower_count': user.count_followers,
            'following_count': user.count_following,
            'minimal': minimal,
            'request': request
        }

    return {
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'username': user['username'],
        'bio': user['profile']['bio'],
        'avatar': user['profile']['avatar'],
        'banner': user['profile']['banner'],
        'following': user['following'],
        'follows_back': user['follows_back'],
        'follower_count': user['count_followers'],
        'following_count': user['count_following'],
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


@register.filter
@defaultfilters.stringfilter
def replace(value, args=","):
    try:
        old, new = args.split(',', 1)
        return value.replace(old, new)
    except ValueError:
        return value
