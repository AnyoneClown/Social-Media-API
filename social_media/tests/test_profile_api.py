from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from social_media.models import Profile
from social_media.serializers import ProfileListSerializer

PROFILE_URL = reverse("social_media:profile-list")


class UnauthenticatedProfileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedProfileApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword"
        )
        self.other_user = get_user_model().objects.create_user(
            "test2@user.com", "testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_profile_list(self):
        Profile.objects.create(user=self.user, bio="My bio")

        response = self.client.get(PROFILE_URL)
        profiles = Profile.objects.all()
        serializer = ProfileListSerializer(profiles, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_owner_required(self):
        other_user_profile = Profile.objects.create(
            user=self.other_user, bio="Other User Bio"
        )

        url = reverse("social_media:profile-detail", args=[other_user_profile.id])

        response = self.client.put(url, {"bio": "Updated Bio"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
