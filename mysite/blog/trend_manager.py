import os

from django.contrib.auth import get_user_model
from django.db.models import Sum
from .models import Post
from apscheduler.schedulers.background import BackgroundScheduler


class TrendManager:
    def __init__(self, interval):
        self.upcoming_posts = None
        self.trending_posts = None
        self.trending_authors = None
        self.scheduler = None
        self.interval = interval
        print('CREATED TREND MANAGER')

    def update(self):
        os.system('cls')
        if self.upcoming_posts:
            self.trending_posts = self.upcoming_posts

        if bool(self.trending_posts):
            print('trending_posts {}'.format(bool(self.trending_posts)))
            post_authors = set(self.trending_posts.values('author').values_list('author_id', flat=True))
            print(post_authors)
            if post_authors:
                print("----------------------------")
                self.trending_authors = get_user_model().objects.filter(pk__in=post_authors).annotate(
                    total_views=Sum('blog_posts__hourly_views')).order_by('-total_views')
        self.upcoming_posts = Post.objects.filter(status=1)
        for post in self.upcoming_posts:
            post.hourly_views = post.views - post.last_views_snapshot or 0
            post.last_views_snapshot = post.views
            post.save()

        self.upcoming_posts = self.upcoming_posts.filter(hourly_views__gt=0).order_by('-hourly_views')


        print('-------------trending_posts-----------')
        print(self.trending_posts)
        print('-------------trending_authors-----------')
        print(self.trending_authors)
        print('-------------upcoming_posts-----------')
        print(self.upcoming_posts)

    def clean(self):
        for post in Post.objects.all():
            post.last_views_snapshot = post.views
            post.save()

    def start(self):
        self.clean()
        self.update()
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.update, 'interval', minutes=self.interval)
        self.scheduler.start()
