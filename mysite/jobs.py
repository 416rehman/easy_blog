from apscheduler.schedulers.background import BackgroundScheduler

from blog.models import Post
from users.models import User


def update_trends():
    print("Updating Trends")
    Post.objects.update_trends()
    User.objects.update_trends()


def start():
    Post.objects.reset_snapshot()
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_trends, 'interval', minutes=0.15)
    scheduler.start()
