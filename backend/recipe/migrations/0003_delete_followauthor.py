# Generated by Django 3.2 on 2023-10-20 19:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_auto_20231015_1935'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FollowAuthor',
        ),
    ]
