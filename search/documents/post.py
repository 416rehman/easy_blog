# Name of the Elasticsearch index
from django_elasticsearch_dsl import Index, Document, fields
from django_elasticsearch_dsl_drf.analyzers import edge_ngram_completion
from django_elasticsearch_dsl_drf.compat import KeywordField

from blog.models import Post
from mysite import settings
from search.documents.analyzers import html_strip

__all__ = ('PostDocument',)
INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])

# See Elasticsearch Indices API reference for available settings
INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)


@INDEX.doc_type
class PostDocument(Document):
    """Post Elasticsearch document."""

    title = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'mlt': fields.TextField(analyzer='english'),
            'suggest': fields.CompletionField(),
        }
    )
    slug = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
        }
    )
    updated_on = fields.DateField()
    created_on = fields.DateField()

    excerpt = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
            'mlt': fields.TextField(analyzer='english')
        }
    )

    content = fields.TextField(
        attr="raw_content",
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword'),
        }
    )

    status = fields.IntegerField()

    tags = fields.TextField(
        attr='tags',
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword', multi=True),
            'suggest': fields.CompletionField(multi=True),
        },
        multi=True
    )

    views = fields.IntegerField(
        attr='views'
    )

    reading_time = fields.IntegerField()
    featured_image = fields.TextField(
        analyzer=html_strip,
        fields={
            'raw': fields.TextField(analyzer='keyword')
        }
    )
    author = fields.ObjectField(
        properties={
            'id': fields.IntegerField(attr='id'),
            'username': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.TextField(analyzer='keyword'),
                }
            ),
            'first_name': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.TextField(analyzer='keyword'),
                }
            ),
            'last_name': fields.TextField(
                analyzer=html_strip,
                fields={
                    'raw': fields.TextField(analyzer='keyword'),
                }
            ),

            'profile': fields.ObjectField(
                properties={
                    'bio': fields.TextField(
                        analyzer=html_strip,
                        fields={
                            'raw': KeywordField(),
                        }
                    ),
                    'avatar': fields.FileField(),
                    'banner': fields.FileField(),
                    'github': fields.TextField(),
                    'linkedin': fields.TextField(),
                    'website': fields.TextField(),
                }
            ),
        }
    )

    class Django(object):
        """Inner nested class Django."""

        model = Post  # The model associate with this Document
