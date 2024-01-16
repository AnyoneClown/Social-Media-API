from rest_framework import serializers

from social_media.models import Profile


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("bio", "profile_picture", "created_at")


class ProfileListSerializer(ProfileSerializer):
    user_email = serializers.CharField(source="user.email")

    class Meta:
        model = Profile
        fields = ("id", "bio", "user_email", "profile_picture", "created_at")