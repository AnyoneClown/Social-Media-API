from django.urls import path, include
from rest_framework import routers

from social_media.views import ProfileViewSet, FollowViewSet, PostViewSet, my_posts, following_posts

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("posts", PostViewSet)
router.register("follows", FollowViewSet)

urlpatterns = [
    path("", include(router.urls))
]

urlpatterns += [
    path("my-posts/", my_posts, name="my-posts"),
    path("following-posts/", following_posts, name="following-posts"),
]

app_name = "social_media"
