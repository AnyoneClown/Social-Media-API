from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from Social_Media_API import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls", namespace="users")),
    path("api/social-media/", include("social_media.urls", namespace="social_media")),
    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
