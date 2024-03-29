from datetime import datetime

from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.tasks import create_post
from social_media.models import Profile, Follow, Post, Like, Commentary
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    ProfileDetailSerializer,
    FollowProfileSerializer,
    FollowingSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentaryPostSerializer,
    CommentarySerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user").prefetch_related("followers")
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Retrieve the profiles with filters"""
        queryset = self.queryset

        bio = self.request.query_params.get("bio")
        created_at = self.request.query_params.get("created_at")
        user_email = self.request.query_params.get("user_email")

        if bio:
            queryset = queryset.filter(bio__icontains=bio)

        if created_at:
            queryset = queryset.filter(created_at__date=created_at)

        if user_email:
            queryset = queryset.filter(user__email__icontains=user_email)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        if self.action == "retrieve":
            return ProfileDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user_email",
                type=OpenApiTypes.STR,
                description="Filter by profile user email (ex. ?user_email=admin@gmail.com)",
            ),
            OpenApiParameter(
                "created_at",
                type=OpenApiTypes.STR,
                description="Filter by profile creating date (ex. ?created_at=2023-01-01)",
            ),
            OpenApiParameter(
                "bio",
                type=OpenApiTypes.STR,
                description="Filter by profile bio (ex. ?bio=User)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["POST"],
        url_path="follow-toggle",
        permission_classes=[IsAuthenticated],
    )
    def follow_toggle(self, request, pk=None):
        profile = self.get_object()
        follower = request.user

        if follower == profile.user:
            return Response(
                {"detail": "Cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow_instance, created = Follow.objects.get_or_create(
            user=follower, following=profile
        )

        if not created:
            follow_instance.delete()
            return Response(
                {"detail": "Successfully unfollowed the profile."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Successfully followed the profile."},
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["GET"],
        url_path="followers",
        permission_classes=[IsAuthenticated],
    )
    def followers(self, request, pk=None):
        profile = self.get_object()

        followers = Follow.objects.filter(following__user=profile.user).select_related(
            "user", "following"
        )
        serializer = FollowProfileSerializer(followers, many=True)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["GET"],
        url_path="following",
        permission_classes=[IsAuthenticated],
    )
    def following(self, request, pk=None):
        profile = self.get_object()

        following_profiles = Follow.objects.filter(user=profile.user).select_related(
            "user", "following"
        )
        serializer = FollowingSerializer(following_profiles, many=True)

        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.prefetch_related(
        "likes__user", "commentaries__user"
    ).select_related("user")
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Retrieve the posts with filters"""
        queryset = self.queryset

        owner = self.request.query_params.get("owner")
        title = self.request.query_params.get("title")
        created_at = self.request.query_params.get("created_at")
        content = self.request.query_params.get("user_email")

        if owner:
            queryset = queryset.filter(owner__icontains=owner)

        if title:
            queryset = queryset.filter(title__icontains=title)

        if created_at:
            queryset = queryset.filter(created_at__date=created_at)

        if content:
            queryset = queryset.filter(content__icontains=content)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by post title (ex. ?title=War)",
            ),
            OpenApiParameter(
                "owner",
                type=OpenApiTypes.STR,
                description="Filter by post owner (ex. ?owner=admin@gmail.com)",
            ),
            OpenApiParameter(
                "content",
                type=OpenApiTypes.STR,
                description="Filter by post content (ex. ?content=USA)",
            ),
            OpenApiParameter(
                "created_at",
                type=OpenApiTypes.STR,
                description="Filter by post created date (ex. ?created_at=2021-01-01)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["GET"],
        url_path="my-posts",
        permission_classes=[IsAuthenticated],
    )
    def my_posts(self, request):
        user = request.user

        posts = Post.objects.filter(user=user)
        serializer = PostListSerializer(posts, many=True)

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        url_path="following-posts",
        permission_classes=[IsAuthenticated],
    )
    def following_posts(self, request):
        user = request.user

        following_users = Follow.objects.filter(user=user).values_list(
            "following__user", flat=True
        )

        posts = Post.objects.filter(user__in=following_users)
        serializer = PostListSerializer(posts, many=True)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["POST"],
        url_path="like-toggle",
        permission_classes=[IsAuthenticated],
    )
    def like_toggle(self, request, pk=None):
        post = self.get_object()
        user = request.user

        like_instance, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            like_instance.delete()
            return Response(
                {"detail": "Successfully unliked the post."}, status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Successfully liked the post."}, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="add-comment",
        permission_classes=[IsAuthenticated],
    )
    def add_comment(self, request, pk=None):
        post = self.get_object()
        data = request.data.copy()

        data.update({"user": request.user.id})
        serializer = CommentaryPostSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        Commentary.objects.create(
            user=request.user, post=post, content=serializer.validated_data["content"]
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["POST"],
        url_path="schedule-post-creation",
        permission_classes=[IsAuthenticated],
    )
    def schedule_post_creation(self, request):
        scheduled_time = request.data.get("scheduled_time")
        scheduled_time = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S.%f%z")

        data = request.data.copy()
        data.update({"user": request.user.id})

        serializer = PostSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        if scheduled_time < timezone.now():
            return Response(
                {"error": "Scheduled data must be in the future"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_post.apply_async(
            args=[
                serializer.validated_data.get("user"),
                serializer.validated_data.get("title"),
                serializer.validated_data.get("content"),
                scheduled_time,
            ],
            eta=scheduled_time,
        )

        return Response(
            {
                "message": f'Post "{serializer.validated_data.get("title")}" scheduled for {scheduled_time}'
            },
            status=status.HTTP_200_OK,
        )


class CommentaryViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Commentary.objects.select_related("user", "post")
    serializer_class = CommentarySerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return CommentaryPostSerializer
        return self.serializer_class
