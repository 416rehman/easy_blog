from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core import mail
from django.core.mail import send_mass_mail, get_connection, EmailMultiAlternatives
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.html import strip_tags
from django.utils.text import slugify
from hitcount.models import HitCount
from tinymce.models import HTMLField


STATUS = (
    (0, "Draft"),
    (1, "Published")
)

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    excerpt = models.TextField(max_length=200, blank=False, null=False)
    content = HTMLField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    taglist = models.TextField(max_length=200, blank=True, null=True)
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')
    hourly_views = models.IntegerField(editable=False, default=0)
    last_views_snapshot = models.IntegerField(editable=False, default=0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    @property
    def views(self):
        return sum([hit_count_generic.hits for hit_count_generic in self.hit_count_generic.all()])

    @property
    def tags(self):
        return [tag.strip() for tag in self.taglist.split(',')] if self.taglist else []

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, slugify(self.title))
        super().save(*args, **kwargs)


class Profile(models.Model):  # add this class and the following fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=250, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to="images/profile/", default="images/profile"
                                                                                           "/default.jpg")
    github = models.URLField(max_length=200, null=True, blank=True)
    linkedin = models.URLField(max_length=200, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.user)

    @receiver(post_save, sender=User)  # add this
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)  # add this
    def save_user_profile(sender, instance, **kwargs):
        if not instance.profile.avatar:
            instance.profile.avatar = "images/profile/default.jpg"
        instance.profile.save()


REASON = (
    (0, "Other"),
    (1, "Hateful or Harassment"),
    (2, "Sexual or Inappropriate"),
    (3, "Spam or Misleading")
)


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_users', null=True, blank=True)
    article = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reported_posts', null=True, blank=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_by', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    reason = models.IntegerField(choices=REASON, default=0)
    comment = models.TextField(max_length=250, null=True, blank=True)
    closing_comment = models.TextField(null=True, blank=True)
    send_follow_up = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        send_follow_up = self.send_follow_up
        send_initial_email = not self.pk
        self.send_follow_up = False
        super().save(*args, **kwargs)

        # follow up closing_comment
        if self.closing_comment and send_follow_up and self.reporter.email:
            context = {
                'username': self.reporter,
                'p1': "We wanted to follow-up with you regarding " + ('an article' if self.article else 'a user') +
                      " report you submitted on " + str(self.created_on.date()) +
                      (", with the following comment \"" + str(self.comment) + "\" " if self.comment else "."),
                'p2': self.closing_comment,
            }
            subject = 'Follow-up on your report'
            html_message = render_to_string('email_templates/static_email_template.html', {'context': context})
            plain_message = strip_tags(html_message)
            from_email = 'Easy Blog <' + settings.DEFAULT_FROM_EMAIL + '>'
            to = self.reporter.email
            mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

        # initial email
        if send_initial_email and self.reporter.email:
            print('Report created email sent')
            context = {
                'username': self.reporter,
                'p1': "We want to thank you for reporting " + ('an article' if self.article else 'a user') +
                      " on our platform. ",
                'p2': "After we have reviewed your report, you might receive a follow-up.",
            }
            subject = 'Your report has been received'
            html_message = render_to_string('email_templates/static_email_template.html', {'context': context})
            plain_message = strip_tags(html_message)
            from_email = 'Easy Blog <' + settings.DEFAULT_FROM_EMAIL + '>'
            to = self.reporter.email
            mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    def delete(self, using=None, keep_parents=False):
        super(Report, self).delete(using=using, keep_parents=keep_parents)
        print('parent is gone and so is this report')
        print(self.reporter.email)

    def __str__(self):
        return str(self.pk)


@receiver(post_delete, sender=Post)
def follow_up_post_reports(sender, instance, **kwargs):
    reports = Report.objects.filter(article=instance)
    reporters = set()
    if reports:
        for r in reports:
            if r.reporter.email:
                reporters.add(r.reporter)

        if reporters:
            messages = []
            for reporter in reporters:
                context = {"username": reporter.username,
                           "p1": 'The article you reported has been removed. The article can be found below',
                           "lines": ['Title: ' + instance.title,
                                     'Excerpt: ' + instance.excerpt],
                           "p2": 'Thank you for your report.'
                           }
                messages.append(('Your report has been received',
                                 'Hi ' + reporter.username + '\n\nThe article you reported has been removed.\n\n Title: ' + instance.title + '\n Excerpt: ' + instance.excerpt + ' \n\nThank you for your report. \n\nSincerely, \nEasy Blog by Ahmadz.ai ',
                                 render_to_string('email_templates/static_email_template.html', {'context': context}),
                                 'Easy Blog <' + settings.DEFAULT_FROM_EMAIL + '>',
                                 [reporter.email]))

            send_mass_html_mail(messages, fail_silently=False)



def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None,
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)



def unique_slugify(instance, slug):
    model = instance.__class__
    unique_slug = slug
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = slug + get_random_string(length=4)
    return unique_slug

