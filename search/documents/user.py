# Name of the Elasticsearch index
from django.contrib.auth import get_user_model
from django_elasticsearch_dsl import Index, Document, fields
from django_elasticsearch_dsl_drf.analyzers import edge_ngram_completion
from django_elasticsearch_dsl_drf.compat import KeywordField

User = get_user_model()
from mysite import settings
from search.documents.analyzers import html_strip

__all__ = ('UserDocument',)
INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)


@INDEX.doc_type
class UserDocument(Document):
    """User Elasticsearch document."""

    id = fields.IntegerField(attr='id')

    username = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'mlt': fields.TextField(analyzer='english'),
            'suggest': fields.CompletionField(),
            'edge_ngram_completion': fields.TextField(
                analyzer=edge_ngram_completion
            ),
        }
    )
    first_name = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'mlt': fields.TextField(analyzer='english'),
            'suggest': fields.CompletionField(),
        }
    )
    last_name = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'mlt': fields.TextField(analyzer='english'),
            'suggest': fields.CompletionField(),
        }
    )

    profile = fields.ObjectField(
        properties={
            'bio': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                    'mlt': fields.TextField(analyzer='english'),
                }
            ),
            'avatar': fields.FileField(),
            'banner': fields.FileField(),
            'github': fields.TextField(),
            'linkedin': fields.TextField(),
            'website': fields.TextField(),
        }
    )

    followers = fields.ObjectField(
        properties={
            'username': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': KeywordField(),
                }
            ),
        }
    )

    count_followers = fields.IntegerField(
        attr='count_followers'
    )
    count_following = fields.IntegerField(
        attr='count_following'
    )

    class Django(object):
        """Inner nested class Django."""

        model = User  # The model associate with this Document
