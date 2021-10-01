from . import views
from django.urls import path

urlpatterns = [
    path('', views.TrendingArticlesView, name='home'),
    path('authors/', views.TrendingAuthorsView, name='home_authors'),
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('@<str:username>/', views.ProfileView, name="profile_page"),
    path('@<str:username>/edit', views.EditProfileView, name="edit_profile"),
    path('write/', views.NewPostView, name='new_post'),
    path('create/', views.CreatePostView, name='create_post'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/edit', views.EditPostView, name='edit_post'),
    path('<slug:slug>/publish', views.PublishPostView, name='publish_post'),
    path('<slug:slug>/unpublish', views.UnpublishPostView, name='unpublish_post'),
    path('<slug:slug>/delete', views.DeletePostView, name='delete_post'),
    path('<slug:slug>/report', views.ReportArticleView, name='report_post'),
]
