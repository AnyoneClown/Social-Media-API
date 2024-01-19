from django.shortcuts import render
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .tasks import create_post


from social_media.models import Profile, Follow, Post, Like, Commentary
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import ProfileSerializer, ProfileListSerializer, FollowSerializer, FollowListSerializer, \
    ProfileDetailSerializer, FollowProfileSerializer, FollowingSerializer, PostSerializer, PostListSerializer, \
    PostDetailSerializer, CommentaryPostSerializer


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

    @action(detail=True, methods=["GET"], url_path="follow-toggle", permission_classes=[IsAuthenticated])
    def follow_toggle(self, request, pk=None):
        profile = self.get_object()
        follower = request.user

        if follower == profile.user:
            return Response({"detail": "Cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        follow_instance, created = Follow.objects.get_or_create(user=follower, following=profile)

        if not created:
            follow_instance.delete()
            return Response({"detail": "Successfully unfollowed the profile."}, status=status.HTTP_200_OK)

        return Response({"detail": "Successfully followed the profile."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["GET"], url_path="followers", permission_classes=[IsAuthenticated])
    def followers(self, request, pk=None):
        profile = self.get_object()

        followers = Follow.objects.filter(following__user=profile.user).select_related("user", "following")
        serializer = FollowProfileSerializer(followers, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["GET"], url_path="following", permission_classes=[IsAuthenticated])
    def following(self, request, pk=None):
        profile = self.get_object()

        following_profiles = Follow.objects.filter(user=profile.user).select_related("user", "following")
        serializer = FollowingSerializer(following_profiles, many=True)

        return Response(serializer.data)


class FollowViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    queryset = Follow.objects.select_related("user", "following", "following__user")
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return FollowListSerializer
        return self.serializer_class


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.prefetch_related("likes__user", "commentaries__user").select_related("user")
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

    @action(detail=False, methods=["GET"], url_path="my-posts", permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        user = request.user

        posts = Post.objects.filter(user=user)
        serializer = PostListSerializer(posts, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="following-posts", permission_classes=[IsAuthenticated])
    def following_posts(self, request):
        user = request.user

        following_users = Follow.objects.filter(user=user).values_list("following__user", flat=True)

        posts = Post.objects.filter(user__in=following_users)
        serializer = PostListSerializer(posts, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["GET"], url_path="like-toggle", permission_classes=[IsAuthenticated])
    def like_toggle(self, request, pk=None):
        post = self.get_object()
        user = request.user

        like_instance, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            like_instance.delete()
            return Response({"detail": "Successfully unliked the post."}, status=status.HTTP_200_OK)

        return Response({"detail": "Successfully liked the post."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"], url_path="add-comment", permission_classes=[IsAuthenticated])
    def add_comment(self, request, pk=None):
        post = self.get_object()

        content = request.data.get("content")

        if not content:
            return Response({"error": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

        comment = Commentary.objects.create(user=request.user, post=post, content=content)
        serializer = CommentaryPostSerializer(comment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"], url_path="schedule-post-creation", permission_classes=[IsAuthenticated])
    def schedule_post_creation(self, request):
        user_id = request.user.id
        title = request.data.get('title')
        content = request.data.get('content')
        scheduled_time = request.data.get('scheduled_time')

        if not title or not content or not scheduled_time:
            return Response({"error": "Missing required data"}, status=status.HTTP_400_BAD_REQUEST)

        create_post.apply_async(args=[user_id, title, content, scheduled_time], eta=scheduled_time)

        return Response({'message': f'Post "{title}" scheduled for {scheduled_time}'}, status=status.HTTP_200_OK)
