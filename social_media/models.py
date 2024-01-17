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
    followers = models.ManyToManyField("Follow", related_name="profiles")
    posts = models.ManyToManyField("Post", related_name="profiles")

    def __str__(self) -> str:
        return self.user.email


class Follow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follows",
    )
    following = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="follows",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    title = models.CharField(max_length=255)
    image = models.ImageField(null=True, upload_to=post_image_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("Like", related_name="post_likes")
    commentaries = models.ManyToManyField("Commentary", related_name="post_commentaries")


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="like_users",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Commentary(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commentary_users",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_commentary"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
