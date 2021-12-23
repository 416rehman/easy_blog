from . import views
from django.urls import path

urlpatterns = [
    path('', views.TrendingPostsView, name='home'),
    path('authors/', views.TrendingAuthorsView, name='home_authors'),
    path('write/', views.NewPostView, name='new_post'),
    path('create/', views.CreatePostView, name='create_post'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/edit', views.EditPostView, name='edit_post'),
    path('<slug:slug>/publish', views.PublishPostView, name='publish_post'),
    path('<slug:slug>/unpublish', views.UnpublishPostView, name='unpublish_post'),
    path('<slug:slug>/delete', views.DeletePostView, name='delete_post'),
    path('<slug:slug>/report', views.ReportPostView, name='report_post'),
]
