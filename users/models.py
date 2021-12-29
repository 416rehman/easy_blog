# Create your models here.
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from django.conf import settings

from blog.models import Post, Profile
from users.tokens import account_activation_token
from django.contrib.auth.models import AbstractUser, UserManager


class UsersManager(UserManager):
    trending = None

    def update_trends(self):
        print('AUTHORS TRENDS UPDATING')
        if Post.objects.trending:
            print('trending_posts {}'.format(bool(Post.objects.trending)))
            post_authors = set(Post.objects.trending.values('author').values_list('author_id', flat=True))
            print(post_authors)
            if post_authors:
                print("----------------------------")
                self.trending = get_user_model().objects.filter(pk__in=post_authors).annotate(
                    total_views=Sum('blog_posts__hourly_views')).order_by('-total_views')


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True)
    objects = UsersManager()
    last_activation_email_sent = models.DateTimeField(null=True, default=timezone.now)

    class Meta:
        db_table = 'auth_user'

    @property
    def count_followers(self):
        return self.followers.count()

    @property
    def count_following(self):
        return User.objects.filter(followers=self).count()

    def is_followed_by(self, username):
        return self.followers.filter(username=username).exists()

    def follow(self, user_to_follow):
        return user_to_follow.followers.add(self)

    def unfollow(self, user_to_unfollow):
        return user_to_unfollow.followers.remove(self)

    def save(self, *args, **kwargs):
        if self.pk:
            if self.email != self.__class__.objects.get(pk=self.pk).email:
                self.is_email_verified = False
        else:
            if not self.is_email_verified and self.email:
                self.send_activation_email()

        super(User, self).save(*args, **kwargs)

    def send_activation_email(self):
        print('SENDING ACTIVATION EMAIL')
        mail_subject = 'Verify your email'
        message = render_to_string('email_templates/account_activation_email.html', {
            'user': self,
            'uid': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': account_activation_token.make_token(self),
            'default_domain': settings.DEFAULT_DOMAIN
        })
        to_email = self.email

        if send_mail(mail_subject, strip_tags(message), 'Easy Blog <' + settings.DEFAULT_FROM_EMAIL + '>', [to_email],
                  html_message=message, fail_silently=False):
            self.last_activation_email_sent = timezone.now()
            self.save()
            print('ACTIVATION EMAIL SENT TO {}'.format(to_email))
        else:
            print('ACTIVATION EMAIL NOT SENT TO {}'.format(to_email))


@receiver(post_save, sender=get_user_model())  # add this
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())  # add this
def save_user_profile(sender, instance, **kwargs):
    if not instance.profile.avatar:
        instance.profile.avatar = "images/profile/default.jpg"
    instance.profile.save()
