from rest_framework import serializers


from social_media.models import Profile, Follow, Post, Like, Commentary


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("bio", "profile_picture", "created_at")

    def validate(self, data):
        user = self.context["request"].user

        if Profile.objects.filter(user=user).exists():
            raise serializers.ValidationError("Profile already exists for this user")

        return data


class ProfileListSerializer(ProfileSerializer):
    user_email = serializers.CharField(source="user.email")

    class Meta:
        model = Profile
        fields = ("id", "bio", "user_email", "profile_picture", "created_at")


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
        fields = (
            "id",
            "bio",
            "user_email",
            "profile_picture",
            "created_at",
            "followers",
        )


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "content", "image")


class PostListSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="user.email")

    class Meta:
        model = Post
        fields = ("id", "owner", "title", "content", "image", "created_at")


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("user", "created_at")


class CommentaryPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentary
        fields = ("user", "content", "created_at")


class PostDetailSerializer(serializers.ModelSerializer):
    likes = LikePostSerializer(many=True, read_only=True, source="post_likes")
    commentaries = CommentaryPostSerializer(
        many=True, read_only=True, source="post_commentary"
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "image",
            "created_at",
            "likes",
            "commentaries",
        )


class CommentarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentary
        fields = ("id", "user", "post", "content", "created_at")
