from rest_framework import serializers

from social_media.models import Profile, Follow


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("bio", "profile_picture", "created_at")

    def validate(self, data):
        user = self.context["request"].user

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


class FollowSerializer(serializers.ModelSerializer):

    def validate(self, data):
        user = self.context["request"].user
        following = data.get("following")

        if user == following.user:
            raise serializers.ValidationError("Cannot follow yourself.")

        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError("Already following this user.")

        return data

    class Meta:
        model = Follow
        fields = ("following",)


class FollowListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email")
    following = serializers.CharField(source="following.user.email")

    class Meta:
        model = Follow
        fields = ("id", "user", "following")


class FollowProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email")

    class Meta:
        model = Follow
        fields = ("user",)


class FollowingSerializer(serializers.ModelSerializer):
    profile = serializers.CharField(source="following.user.email")

    class Meta:
        model = Follow
        fields = ("profile", "created_at")


class ProfileDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email")
    followers = FollowProfileSerializer(many=True, read_only=True, source="follows")

    class Meta:
        model = Profile
        fields = ("id", "bio", "user_email", "profile_picture", "created_at", "followers")
