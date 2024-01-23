from django.urls import path
from users.views import CreateTokenView, CreateUserView, LogoutView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", CreateTokenView.as_view(), name="token"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

app_name = "users"
