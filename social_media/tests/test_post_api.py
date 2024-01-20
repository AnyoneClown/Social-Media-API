from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from social_media.models import Post, Like
from social_media.serializers import PostListSerializer, PostDetailSerializer

POST_URL = reverse("social_media:post-list")
POST_LIKE_URL = reverse("social_media:post-like-toggle", args=[1])


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(POST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPostApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_post_list(self):
        Post.objects.create(user=self.user, title="Test Title", content="Test Content")

        response = self.client.get(POST_URL)
        posts = Post.objects.all()
        serializer = PostListSerializer(posts, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_post_retrieve(self):
        test_post = Post.objects.create(
            user=self.user, title="Test Title", content="Test Content"
        )

        url = reverse("social_media:post-detail", args=[test_post.id])

        response = self.client.get(url)
        serializer = PostDetailSerializer(test_post)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_owner_required(self):
        other_user_post = Post.objects.create(
            user=get_user_model().objects.create_user("test2@user.com", "testpassword"),
            title="Other User Post",
            content="Other User Content",
        )

        url = reverse("social_media:post-detail", args=[other_user_post.id])

        response = self.client.put(url, {"title": "Updated Title"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LikeToggleActionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword"
        )
        self.client.force_authenticate(self.user)
        self.post = Post.objects.create(
            user=self.user, title="Test Title", content="Test Content"
        )

    def test_like_toggle(self):
        response = self.client.get(POST_LIKE_URL)

        updated_post = Post.objects.get(pk=self.post.id)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        if Like.objects.filter(user=self.user, post=self.post).exists():
            self.assertEqual(response.data["detail"], "Successfully liked the post.")
            self.assertFalse(updated_post.likes.filter(user=self.user).exists())
        else:
            self.assertEqual(response.data["detail"], "Successfully unliked the post.")
            self.assertTrue(updated_post.likes.filter(user=self.user).exists())
