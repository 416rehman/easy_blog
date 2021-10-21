from django import template

from mysite import settings

register = template.Library()


@register.inclusion_tag('components/profile-card.html')
def profile_card(username, first_name, last_name, bio, avatar, banner):
    return {
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
        'bio': bio,
        'avatar': 'https://s3.amazonaws.com/' + settings.AWS_STORAGE_BUCKET_NAME + '/' + settings.AWS_PUBLIC_MEDIA_LOCATION + '/' + str(
            avatar),
        'banner': 'https://s3.amazonaws.com/' + settings.AWS_STORAGE_BUCKET_NAME + '/' + settings.AWS_PUBLIC_MEDIA_LOCATION + '/' + str(
            banner)
    }


@register.inclusion_tag('components/post-card.html')
def post_card(post):
    return {
        'post': post,
    }
