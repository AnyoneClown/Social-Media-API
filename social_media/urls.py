from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers

from social_media.views import ProfileViewSet

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "social_media"
