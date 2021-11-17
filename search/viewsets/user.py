import datetime
import re
from json import dumps, loads

from django.shortcuts import redirect, render
from django.utils.decorators import classonlymethod
from rest_framework.decorators import action

from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION, LOOKUP_FILTER_RANGE, LOOKUP_QUERY_GT, \
    LOOKUP_QUERY_GTE, LOOKUP_QUERY_LT, LOOKUP_QUERY_LTE
from django_elasticsearch_dsl_drf.filter_backends import FilteringFilterBackend, \
    OrderingFilterBackend, DefaultOrderingFilterBackend, \
    SuggesterFilterBackend, CompoundSearchFilterBackend
from django_elasticsearch_dsl_drf.pagination import QueryFriendlyPageNumberPagination
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet

from ..documents.user import UserDocument
from ..serializers.user import UserDocumentSerializer


class UserDocumentViewSet(DocumentViewSet):
    """The UserDocument view"""

    document = UserDocument
    serializer_class = UserDocumentSerializer
    lookup_field = 'username'
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        CompoundSearchFilterBackend,
        DefaultOrderingFilterBackend,
        SuggesterFilterBackend,
    ]
    pagination_class = QueryFriendlyPageNumberPagination
    search_fields = {
        'username': {'fuzziness': 'AUTO'},
        'first_name': {'fuzziness': 'AUTO'},
        'last_name': {'fuzziness': 'AUTO'},
        'profile.bio': None,
        'profile.github': None,
        'profile.website': None,
        'profile.linkedin': None
    }

    filter_fields = {
        'count_followers': {
            'field': 'count_followers',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'count_following': {
            'field': 'count_following',
            'lookups': [
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
    }

    # Define ordering fields
    ordering_fields = {
        'count_followers': None,
        'count_following': None,
    }

    ordering = (
        '_score',
        'count_followers',
        'count_following'
    )
    suggester_fields = {
        'username_suggest': {
            'field': 'tags.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION
            ],
        },
        'first_name_suggest': {
            'field': 'first_name.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION
            ]
        },
        'last_name_suggest': {
            'field': 'last_name.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION
            ]
        }
    }


class UserCustomDocumentViewSet(UserDocumentViewSet):
    page_size = 1

    @classonlymethod
    def as_view(cls, actions=None, **initkwargs):
        # No request object is available here

        return super(UserCustomDocumentViewSet, cls).as_view(
            actions,
            **initkwargs
        )

    def retrieve(self, request, *args, **kwargs):
        # Used for detail routes, like
        # http://localhost:8000/search/user/watchdogsrox/
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

        if query and field:
            if field in self.search_fields:
                request.GET['search'] = '{field}:{query}'.format(field=request.GET['in_field'] if request.GET['in_field'] != 'all' else '',
                                                                 query=query.split(':')[1] if ':' in query else query)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

        request.GET['search'] = query

        paginator = {
            'next': response.data['next'],
            'previous': response.data['previous'],
            'count': response.data['count'],
            'current_page': request.GET['page']
        }
        results = loads(dumps(response.data['results'])) or {}
        for r in results:
            r['following'] = {}
            r['follows_back'] = {}
            if request.user.is_authenticated:
                for follower in r['followers']:
                    r['following'] = True if follower['username'] == request.user.username else False
                r['follows_back'] = (request.user.followers.filter(username=r['username']).exists())


        search_url = re.sub('&*(?:page=)\d*', '', request.get_full_path())
        return render(request, 'user_search.html',
                      {'results': results, 'paginator': paginator, 'facets': response.data['facets'],
                       'search_url': search_url})

    @action(detail=False)
    def suggest(self, request):
        # Used for suggest routes, like
        # http://localhost:8000/search/books-custom/suggest/?title_suggest=A

        return super(UserCustomDocumentViewSet, self).suggest(
            request
        )
