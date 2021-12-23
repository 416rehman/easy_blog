from . import views
from django.urls import path

urlpatterns = [
    path('auth/signup/', views.SignUpView, name='signup'),
    path('activate', views.InactiveUserView.as_view(), name='inactive_view'),
    path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='verify_email'),
    path('@<str:username>/', views.ProfileView, name="profile_page"),
    path('@<str:username>/posts', views.UserPostsView, name="user_posts"),
    path('@<str:username>/edit', views.EditProfileView, name="edit_profile"),
    path('@<str:username>/report', views.ReportUserView, name="report_user"),
    path('@<str:username>/follow', views.AJAX_FollowUserView, name="follow_user"),
    path('@<str:username>/followers', views.UserFollowersView, name="followers"),
    path('@<str:username>/following', views.UserFollowingView, name="following"),
]
