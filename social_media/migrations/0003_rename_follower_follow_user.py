# Generated by Django 5.0.1 on 2024-01-17 00:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("social_media", "0002_follow_profile_followers"),
    ]

    operations = [
        migrations.RenameField(
            model_name="follow",
            old_name="follower",
            new_name="user",
        ),
    ]