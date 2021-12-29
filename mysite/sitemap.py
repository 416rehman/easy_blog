# create a sitemap class
from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from blog.models import Post
from users.models import User


class PostSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        # return only published posts
        return Post.objects.filter(status=1)

    def location(self, obj):
        return reverse('post_detail', kwargs={'slug': obj.slug})

    def lastmod(self, obj):
        return obj.updated_on


class UserSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return User.objects.filter(is_active=True)

    def location(self, obj):
        return reverse('profile_page', kwargs={'username': obj.username})


# create a generic sitemap
class StaticSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['home', 'new_post', 'login', 'signup', 'logout', 'password_reset', ]

    def location(self, item):
        return reverse(item)
