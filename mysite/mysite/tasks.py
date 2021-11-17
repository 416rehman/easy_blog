from django.contrib.auth import get_user_model

from blog.models import Post


def run():
    print('TASKS ADDED')
    Post.objects.update_trends()
    get_user_model().objects.update_trends()
