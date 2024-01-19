from django.urls import path, include
from rest_framework import routers

from social_media.views import ProfileViewSet, PostViewSet, CommentaryViewSet

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("posts", PostViewSet)
router.register("comments", CommentaryViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "social_media"
