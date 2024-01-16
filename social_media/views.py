from django.shortcuts import render
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Profile
from social_media.permissions import IsOwnerOrReadOnly
from social_media.serializers import ProfileSerializer, ProfileListSerializer


class ProfileViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Profile.objects.select_related("user")
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
        if self.action in ("list", "retrieve"):
            return ProfileListSerializer
        return self.serializer_class
