from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Post, Profile


@registry.register_document
class PostDocument(Document):
    author = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'first_name': fields.TextField(),
        'last_name': fields.TextField(),
        'username': fields.TextField(),
    })

    class Index:
        name = 'posts'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Post
        fields = [
            'title',
            'excerpt',
            'taglist'
        ]


@registry.register_document
class UserDocument(Document):
    user = fields.ObjectField(properties={
        'username': fields.TextField(),
        'first_name': fields.TextField(),
        'last_name': fields.TextField(),
    })

    class Index:
        name = 'users'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Profile
        fields = [
            'bio'
        ]
