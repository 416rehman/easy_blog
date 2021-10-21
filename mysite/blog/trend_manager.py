from django.db.models import Sum
from .models import Post
from apscheduler.schedulers.background import BackgroundScheduler


class TrendManager:
    upcoming_posts = None
    trending_posts = None
    trending_authors = None
    scheduler = None

    def update(self):
        print('updating Trends')

        if self.upcoming_posts:
            self.trending_posts = self.upcoming_posts
            if self.trending_posts:
                self.trending_authors = self.trending_posts.values('author', 'author__username', 'author__first_name',
                                                                   'author__last_name', 'author__profile__bio',
                                                                   'author__profile__avatar', 'author__profile__banner').order_by(
                    'author').annotate(total_views=Sum('hourly_views'))
                print(f'Trending Authors: {bool(self.trending_authors)}')

        print(f'Trending Posts: {bool(self.trending_posts)}')

        self.upcoming_posts = Post.objects.filter(status=1)
        for post in self.upcoming_posts:
            post.hourly_views = post.views - post.last_views_snapshot
            post.last_views_snapshot = post.views
            post.save()
        self.upcoming_posts = self.upcoming_posts.filter(hourly_views__gt=0, status=1).order_by('-hourly_views')

    def clean(self):
        for post in Post.objects.all():
            post.last_views_snapshot = post.views
            post.save()

    def start(self, minutes):
        self.clean()
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.update, 'interval', minutes=minutes)
        self.scheduler.start()
