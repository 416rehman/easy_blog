from django.contrib.auth import get_user_model
from django.db.models import Sum
from .models import Post
from apscheduler.schedulers.background import BackgroundScheduler


class TrendManager:
    upcoming_posts = None
    trending_posts = None
    trending_authors = None
    scheduler = None

    def update(self):
        if self.upcoming_posts:
            self.trending_posts = self.upcoming_posts
            if self.trending_posts:
                post_authors = self.trending_posts.values('author').values_list('author', flat=True)
                if post_authors.count():
                    self.trending_authors = get_user_model().objects.filter(pk__in=post_authors).annotate(total_views=Sum('blog_posts__hourly_views')).order_by('-total_views').distinct()
                    print('Trending Authors')
                    print(self.trending_authors)

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
