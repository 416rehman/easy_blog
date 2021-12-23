from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter
from .viewsets import post, user

router = DefaultRouter()
posts = router.register(r'posts',
                        post.PostCustomDocumentViewSet,
                        basename='postdocument')
users = router.register(r'users',
                        user.UserCustomDocumentViewSet,
                        basename='userdocument')
urlpatterns = [
    url(r'^', include(router.urls)),
]
