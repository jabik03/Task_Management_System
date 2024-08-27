from django.contrib.auth.views import LogoutView
from django.urls import path

from authentication import views


app_name = "authentication"

urlpatterns = [
    path("profile/", views.ProfileUser.as_view(), name="profile"),
    
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user_delete"),
]
