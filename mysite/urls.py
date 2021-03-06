"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views

from mysite.sitemap import PostSitemap, UserSitemap, StaticSitemap
from search.urls import urlpatterns as search_index_urls

sitemaps = {
    'static': StaticSitemap,
    'users': UserSitemap,
    'posts': PostSitemap,
}

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('auth/login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
                  path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
                  path('recover/',
                       auth_views.PasswordResetView.as_view(
                           html_email_template_name='email_templates/password_reset_email'
                                                    '.html'), name='password_reset'),
                  path('recover/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
                  path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(),
                       name='password_reset_confirm'),
                  path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
                  path('tinymce/', include('tinymce.urls')),
                  re_path(r'^search/', include(search_index_urls)),
                  path('', include('users.urls')),
                  path('', include('blog.urls')),
                  path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL,
                                                                                         document_root=settings.STATIC_ROOT)
