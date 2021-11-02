import json
import re
from itertools import chain
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic, View
from django.urls import reverse_lazy, reverse
from elasticsearch_dsl import Q
from hitcount.views import HitCountDetailView

from .forms import PostForm, ReportForm
from .models import Post
from django.conf import settings
from django.apps import apps


def TrendingPostsView(request):
    queryset = q_filter = None
    if not request.GET.get('filter') or request.GET.get('filter') == 'trending':
        queryset = apps.get_app_config('blog').trend_manager.trending_posts
        q_filter = 'trending'

    if (not queryset and not request.GET.get('filter') == 'trending') or request.GET.get('filter') == 'new':
        queryset = Post.objects.filter(status=1)
        q_filter = 'new'

    return render(request, 'trending_posts.html', {'posts': queryset, 'filter': q_filter})


def TrendingAuthorsView(request):
    queryset = q_filter = None
    if not request.GET.get('filter') or request.GET.get('filter') == 'trending':
        queryset = apps.get_app_config('blog').trend_manager.trending_authors
        print(queryset)
        q_filter = 'trending'

    if (not queryset and not request.GET.get('filter') == 'trending') or request.GET.get('filter') == 'new':
        queryset = get_user_model().objects.filter(is_active=True).order_by('-date_joined')
        q_filter = 'new'
    return render(request, 'trending_authors.html', {'authors': queryset, 'filter': q_filter})


class PostDetailView(HitCountDetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    count_hit = True

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)

        if context['post'].author != self.request.user and not context['post'].status == 1:
            messages.error(self.request, 'Invalid Post.')
            return None
        return context


def NewPostView(request):
    # if any pre-existing written data is in the session (before authentication), use that.
    form = None
    if 'form_data' in request.session:
        data = json.loads(request.session['form_data'])
        del request.session['form_data']
        form = PostForm(data or None)
    else:
        form = PostForm(request.POST or None)
    return render(request, 'edit_post.html', {'form': form, 'newPost': True})


def CreatePostView(request):
    # if writing without authentication, save the data in session, and re-use it when logged in
    if not request.user.is_authenticated:
        request.session['form_data'] = json.dumps(request.POST)
        return redirect("%s?next=%s" % (settings.LOGIN_URL, reverse('create_post')))

    if request.method == 'GET':
        form = None
        if 'form_data' in request.session:
            data = json.loads(request.session['form_data'])
            del request.session['form_data']
            form = PostForm(data or None)
            return render(request, 'edit_post.html', {'form': form, 'newPost': True})
        else:
            return redirect('new_post')
    else:
        form = PostForm(request.POST or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            messages.add_message(request, messages.SUCCESS, 'Post Created!')
            return redirect('post_detail', slug=obj.slug)
        else:
            for e in form.errors:
                messages.add_message(request, messages.ERROR, e)
            return render(request, 'edit_post.html', {'form': form, 'newPost': True})


@login_required
def EditPostView(request, slug):
    instance = get_object_or_404(Post, slug=slug)

    if instance.author != request.user:
        return redirect('post_detail', slug=slug)

    form = PostForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, 'Post updated!')
        return redirect('post_detail', slug=slug)
    return render(request, 'edit_post.html', {'form': form})


@login_required
def PublishPostView(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    if instance.author == request.user:
        instance.status = 1
        instance.save()
        messages.success(request, 'Your post has been published.')
        return redirect('post_detail', slug=slug)

    messages.success(request, 'An error occured while publishing the post.')
    return render(request, 'index.html')


@login_required
def UnpublishPostView(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    if instance.author == request.user:
        instance.status = 0
        instance.save()
        messages.success(request, 'Your post has been unpublished.')
        return redirect('post_detail', slug=slug)

    messages.success(request, 'An error occured while unpublishing the post.')
    return render(request, 'index.html')


@login_required
def DeletePostView(request, slug):
    instance = get_object_or_404(Post, slug=slug)
    if instance.author == request.user:
        instance.delete()
        messages.success(request, 'Deleted Post')
        return redirect('profile_page', username=request.user.username)

    messages.success(request, 'An error occured while deleting the post.')
    return render(request, 'index.html')


@login_required
def ReportPostView(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author == request.user:
        return redirect('post_detail', slug=slug)
    if post:
        postReportForm = ReportForm(request.POST or None)

        if postReportForm.is_valid():
            new_report = postReportForm.save(commit=False)
            new_report.post = post
            if request.user:
                new_report.reporter = request.user
            new_report.save()

            messages.add_message(request, messages.SUCCESS, 'Post Reported')
            return redirect('post_detail', slug=slug)

        return render(request, 'report.html', context={'form': postReportForm})
