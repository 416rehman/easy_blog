from apscheduler.schedulers.background import BackgroundScheduler
from blog.models import Post

class Trends:
    def __init__(self):
        self.current_posts = None
        self.upcoming_posts = None
        self.current_authors = None
        self.test = "OG"

    def update_posts(self):
        self.test = "UPDATED"
        if self.upcoming_posts:
            self.current_posts = self.upcoming_posts
        print('---------trending POSTS------------')
        print(self.current_posts)

        self.upcoming_posts = Post.objects.filter(status=1)
        for post in self.upcoming_posts:
            post.hourly_views = post.views - post.last_views_snapshot or 0
            post.last_views_snapshot = post.views
            post.save()
        self.upcoming_posts = self.upcoming_posts.filter(hourly_views__gt=0).order_by('-hourly_views')
        print('---------upcoming_posts------------')
        print(self.upcoming_posts)

    def reset_snapshot(self):
        for post in Post.objects.all():
            post.last_views_snapshot = post.views
            post.save()

    def update_authors(self):
        if self.current_posts:
            post_authors = set(self.current_posts.values('author').values_list('author_id', flat=True))
            if post_authors:
                self.current_authors = get_user_model().objects.filter(pk__in=post_authors).annotate(
                    total_views=Sum('blog_posts__hourly_views')).order_by('-total_views')

trending = Trends()

def update_trends():
    print("Updating Trends")
    trending.update_posts()
    trending.update_authors()
    print('=========job==========')
    print(trending.current_posts)
    print(id(trending))
    print(trending.test)

def start():
    trending.reset_snapshot()
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_trends, 'interval', minutes=0.15)
    scheduler.start()
