# Generated by Django 3.2.7 on 2021-10-22 18:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_followers_following_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Followers',
        ),
    ]