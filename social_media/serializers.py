from rest_framework import serializers

from social_media.models import Profile


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("bio", "profile_picture", "created_at")

    def validate(self, data):
        user = self.context['request'].user
        print(user)

        if Profile.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                "Profile already exists for this user"
            )

        return data


class ProfileListSerializer(ProfileSerializer):
    user_email = serializers.CharField(source="user.email")

    class Meta:
        model = Profile
        fields = ("id", "bio", "user_email", "profile_picture", "created_at")