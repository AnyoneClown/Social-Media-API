import os
import uuid

from django.db import models
from django.utils.text import slugify

from Social_Media_API import settings


def profile_image_file_path(instance, filename):
    return image_file_path(instance, filename, "profiles")


def post_image_file_path(instance, filename):
    return image_file_path(instance, filename, "posts")


def image_file_path(instance, filename, folder):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance)}-{uuid.uuid4()}{extension}"
    path = os.path.join("uploads", folder)
    return os.path.join(path, filename)


class Profile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(null=True, upload_to=profile_image_file_path)
    created_at = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    title = models.CharField(max_length=255)
    image = models.ImageField(null=True, upload_to=post_image_file_path)