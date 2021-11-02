__all__ = (
    'UserDocumentSerializer',
)

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from ..documents.user import UserDocument


class UserDocumentSerializer(DocumentSerializer):
    """Serializer for user document."""

    class Meta:
        """Meta options."""

        document = UserDocument
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'profile',
            'followers',
            'count_followers',
            'count_following',
        )