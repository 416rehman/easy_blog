import json
import re
from itertools import chain
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy, reverse
from elasticsearch_dsl import Q
from hitcount.views import HitCountDetailView

from .documents import UserDocument, PostDocument
from .forms import SignupForm, PostForm, ProfileForm, UserForm, ReportArticleForm
from .models import Post
from django.conf import settings
from django.apps import apps


def TrendingArticlesView(request):
    queryset = q_filter = None
    if not request.GET.get('filter') or request.GET.get('filter') == 'trending':
        queryset = apps.get_app_config('blog').trend_manager.trending_posts
        q_filter = 'trending'

    if (not queryset and not request.GET.get('filter') == 'trending') or request.GET.get('filter') == 'new':
        queryset = Post.objects.filter(status=1)
        q_filter = 'new'

    return render(request, 'trending_articles.html', {'articles': queryset, 'filter': q_filter})


def TrendingAuthorsView(request):
    queryset = q_filter = None
    if not request.GET.get('filter') or request.GET.get('filter') == 'trending':
        queryset = apps.get_app_config('blog').trend_manager.trending_authors
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


class SignUpView(generic.CreateView):
    form_class = SignupForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    # Protected route
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super(SignUpView, self).dispatch(request, *args, **kwargs)


def ProfileView(request, username):
    if request.user.username == username:
        user = request.user
        posts = Post.objects.filter(author=user)
    else:
        user = get_user_model().objects.get(username=username)
        posts = Post.objects.filter(author=user, status=1)

    context = {
        'requested_profile': user,
        'posts': posts
    }
    return render(request, 'profile.html', context=context)


def NewPostView(request):
    form = PostForm(request.POST or None)
    return render(request, 'edit_post.html', {'form': form, 'newPost': True})


def CreatePostView(request):
    if not request.user.is_authenticated:
        request.session['form_data'] = json.dumps(request.POST)

        return redirect("%s?next=%s" % (settings.LOGIN_URL, reverse('create_post')))

    if request.method == 'GET':
        if 'form_data' in request.session:
            data = json.loads(request.session['form_data'])
            del request.session['form_data']  # Delete the key once done
            form = PostForm(data or None)
            return render(request, 'edit_post.html', {'form': form, 'newPost': True})
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
def EditProfileView(request, username):
    instance = get_object_or_404(get_user_model(), username=username)

    if instance.username != request.user.username:
        return redirect('profile_page', username=username)

    userForm = UserForm(request.POST or None, instance=instance)
    profileForm = ProfileForm(request.POST or None, instance=instance.profile)
    if request.method == 'POST':
        profileForm = ProfileForm(request.POST or None, request.FILES, instance=instance.profile)

    if userForm.is_valid() and profileForm.is_valid():
        userForm.save()
        profileForm.save()
        messages.add_message(request, messages.SUCCESS, 'Profile updated!')
        return redirect('profile_page', username=username)
    context = {
        'userForm': userForm,
        'profileForm': profileForm
    }
    return render(request, 'edit_profile.html', context=context)


class SearchView(generic.View):
    def get(self, request):
        search_type = request.GET.get('type') or None
        search_sort = request.GET.get('sort') or None
        search_order = request.GET.get('order') or None
        search_scope = request.GET.get('scope') or None
        search_scope = search_scope.split(',') if search_scope else None
        user_qs = post_qs = all_qs = paginator = page_obj = None

        if not search_type or search_type == 'user':
            fields = search_scope if search_scope else [
                'user.username',
                'user.first_name',
                'user.last_name',
                'bio',
            ]
            user_q = Q('multi_match', query=request.GET.get('q'),
                       fields=fields, fuzziness='auto')
            user_search = UserDocument.search().query(user_q)
            user_qs = user_search.to_queryset()

        if not search_type or search_type == 'article':
            fields = search_scope if search_scope else [
                'title',
                'excerpt',
                'taglist',
                'raw_content'
            ]
            post_q = Q('multi_match', query=request.GET.get('q'),
                       fields=fields, fuzziness='auto')
            post_search = PostDocument.search().query(post_q)
            post_qs = post_search.to_queryset()
            post_qs = post_qs.filter(status=1)

        if search_type == 'article' and search_sort and post_qs:
            if search_sort == 'author':
                post_qs = post_qs.order_by('author' if search_order == 'ascending' else '-author')
            elif search_sort == 'date':
                post_qs = post_qs.order_by('created_on' if search_order == 'ascending' else '-created_on')
            elif search_sort == 'title':
                post_qs = post_qs.order_by('title' if search_order == 'ascending' else '-title')
        elif post_qs:  # Default sort by popularity
            post_qs = post_qs.order_by(
                'hit_count_generic__hits' if search_order == 'ascending' else '-hit_count_generic__hits')

        if post_qs and user_qs:
            all_qs = list(chain(user_qs, post_qs))
        elif post_qs:
            all_qs = post_qs
        elif user_qs:
            all_qs = user_qs

        if all_qs:
            paginator = Paginator(all_qs, per_page=5)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number).object_list

        search_url = re.sub('&*(?:page=)\d*', '', request.get_full_path())
        return render(request, 'search.html',
                      {'paginator': paginator or None, 'results': page_obj or None, 'search_url': search_url,
                       'posts_only': not user_qs})


def ReportArticleView(request, slug):
    article = get_object_or_404(Post, slug=slug)
    if article:
        articleReportForm = ReportArticleForm(request.POST or None)

        if articleReportForm.is_valid():
            new_report = articleReportForm.save(commit=False)
            new_report.article = article
            if request.user:
                new_report.reporter = request.user
            new_report.save()

            messages.add_message(request, messages.SUCCESS, 'Article Reported')
            return redirect('post_detail', slug=slug)

        return render(request, 'report_post.html', context={'form': articleReportForm})
