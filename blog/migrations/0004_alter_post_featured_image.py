# Generated by Django 3.2.7 on 2021-10-20 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_alter_post_featured_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='featured_image',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
