# Create your models here.
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from django.conf import settings
from users.tokens import account_activation_token
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'auth_user'

    def save(self, *args, **kwargs):
        if not self.is_email_verified and self.email:
            self.send_activation_email()
        super(User, self).save(*args, **kwargs)

    def send_activation_email(self):
        mail_subject = 'Verify your email'
        message = render_to_string('email_templates/account_activation_email.html', {
            'user': self,
            'uid': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': account_activation_token.make_token(self),
            'default_domain': settings.DEFAULT_DOMAIN
        })
        to_email = self.email
        send_mail(mail_subject, strip_tags(message), 'Easy Blog <' + settings.DEFAULT_FROM_EMAIL + '>', [to_email],
                  html_message=message)


class Followers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    following_user = models.ManyToManyField(User, related_name='following_user', null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=get_user_model())  # add this
def create_followers(sender, instance, created, **kwargs):
    if created:
        Followers.objects.create(user=instance)
