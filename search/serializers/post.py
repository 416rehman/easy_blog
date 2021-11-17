__all__ = (
    'PostDocumentSerializer',
)

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from ..documents.post import PostDocument


class PostDocumentSerializer(DocumentSerializer):
    """Serializer for post document."""

    class Meta:
        """Meta options."""

        document = PostDocument
        fields = (
            'id',
            'title',
            'slug',
            'updated_on',
            'created_on',
            'excerpt',
            'content',
            'status',
            'tags',
            'views',
            'reading_time',
            'author',
            'featured_image'
        )