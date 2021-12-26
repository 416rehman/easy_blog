import datetime
import re

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect, render
from django.urls import resolve
from django.utils.decorators import classonlymethod
from rest_framework.decorators import action

from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION, LOOKUP_FILTER_RANGE, LOOKUP_QUERY_GT, \
    LOOKUP_QUERY_GTE, LOOKUP_QUERY_LT, LOOKUP_QUERY_LTE, LOOKUP_FILTER_TERMS, LOOKUP_FILTER_PREFIX, \
    LOOKUP_FILTER_WILDCARD, LOOKUP_QUERY_IN, LOOKUP_QUERY_EXCLUDE
from django_elasticsearch_dsl_drf.filter_backends import FacetedSearchFilterBackend, FilteringFilterBackend, \
    OrderingFilterBackend, SearchFilterBackend, NestedFilteringFilterBackend, DefaultOrderingFilterBackend, \
    SuggesterFilterBackend, CompoundSearchFilterBackend
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination, QueryFriendlyPageNumberPagination
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from ..documents.post import PostDocument
from ..serializers.post import PostDocumentSerializer


class PostDocumentViewSet(DocumentViewSet):
    """The PostDocument view"""

    document = PostDocument
    serializer_class = PostDocumentSerializer
    lookup_field = 'slug'
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        CompoundSearchFilterBackend,
        DefaultOrderingFilterBackend,
        SuggesterFilterBackend,
    ]
    pagination_class = QueryFriendlyPageNumberPagination
    search_fields = {
        'title': {'fuzziness': 'AUTO'},
        'slug': None,
        'excerpt': None,
        'content': None,
        'tags': None,
        'author.username': None,
        'author.first_name': None,
        'author.last_name': None
    }

    filter_fields = {
        'author': 'author.username.raw',
        'views': {
            'field': 'views',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'updated_on': {
            'field': 'updated_on',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'created_on': {
            'field': 'created_on',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'tags': {
            'field': 'tags.raw',
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },
    }

    # Define ordering fields
    ordering_fields = {
        'updated_on': None,
        'created_on': None,
        'views': None,
        'reading_time': None,
    }
    ordering = (
        '_score',
        'views',
        'updated_on',
    )
    suggester_fields = {
        'tags_suggest': {
            'field': 'tags.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION
            ],
        },
        'title_suggest': {
            'field': 'title.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION
            ]
        }
    }


class PostCustomDocumentViewSet(PostDocumentViewSet):
    page_size = 10

    @classonlymethod
    def as_view(cls, actions=None, **initkwargs):
        # No request object is available here
        return super(PostCustomDocumentViewSet, cls).as_view(
            actions,
            **initkwargs
        )

    def retrieve(self, request, *args, **kwargs):
        # Used for detail routes, like
        # http://localhost:8000/search/books-custom/999999/
        return redirect('home')

    def list(self, request, *args, **kwargs):
        # Used for list routes, like
        # http://localhost:8000/search/books-custom/

        # Force Pagination
        request.GET._mutable = True
        request.GET['page'] = request.GET.get('page', 1)
        request.GET['page_size'] = request.GET.get('page_size', self.page_size)

        # Default Ordering Descending (ordering = field to sort, order = ascending/descending)
        ordering = request.GET.get('ordering', '')
        order = request.GET.get('order', '')
        if ordering and order != 'ascending':
            request.GET['ordering'] = '-' + ordering

        # Field-based search
        field = request.GET.get('in_field', 0)
        query = request.GET.get('search', 0)
        if field and query:
            if field == 'all':
                request.GET['search'] = query.split(':')[1] if ':' in query else query
            else:
                request.GET['search'] = '{field}:{query}'.format(field=request.GET['in_field'],
                                                                 query=query.split(':')[1] if ':' in query else query)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

        paginator = {
            'next': response.data['next'],
            'previous': response.data['previous'],
            'count': response.data['count'],
            'current_page': request.GET['page']
        }
        for post in response.data['results']:
            post['created_on'] = datetime.datetime.strptime(post['created_on'], '%Y-%m-%dT%H:%M:%S.%f%z')
            post['updated_on'] = datetime.datetime.strptime(post['updated_on'], '%Y-%m-%dT%H:%M:%S.%f%z')

        search_url = re.sub('&*(?:page=)\d*', '', request.get_full_path())
        return render(request, 'post_search.html',
                      {'results': response.data['results'], 'paginator': paginator, 'facets': response.data['facets'],
                       'search_url': search_url})

    @action(detail=False)
    def suggest(self, request):
        # Used for suggest routes, like
        # http://localhost:8000/search/books-custom/suggest/?title_suggest=A
        return super(PostCustomDocumentViewSet, self).suggest(
            request
        )
