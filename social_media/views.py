from django.shortcuts import render
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Profile, Follow
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import ProfileSerializer, ProfileListSerializer, FollowSerializer, FollowListSerializer, \
    ProfileDetailSerializer, FollowProfileSerializer, FollowingSerializer


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

    @action(detail=True, methods=["GET"], url_path="follow", permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        profile = self.get_object()
        follower = request.user

        if follower == profile.user:
            return Response({"detail": "Cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        follow_instance, created = Follow.objects.get_or_create(user=follower, following=profile)

        if not created:
            return Response({"detail": "Already following this profile."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Successfully followed the profile."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["GET"], url_path="unfollow", permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        profile = self.get_object()
        follower = request.user

        follow = Follow.objects.filter(user=follower, following=profile).first()

        if not follow:
            return Response({"detail": "Not following this profile."}, status=status.HTTP_400_BAD_REQUEST)

        follow.delete()
        return Response({"detail": "Successfully unfollowed the profile."}, status=status.HTTP_200_OK)

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
