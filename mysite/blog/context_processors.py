from mysite import settings


def default_domain(request):
    return {
        'default_domain': 'https://blog.ahmadz.ai'
    }


def aws_media_url(request):
    return {
        'aws_media_url': 'https://s3.amazonaws.com/' + settings.AWS_STORAGE_BUCKET_NAME + '/' + settings.AWS_PUBLIC_MEDIA_LOCATION + '/'
    }
