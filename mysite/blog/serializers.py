from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    slug = serializers.SlugField()
    excerpt = serializers.CharField(max_length=200)
    created_on = serializers.DateTimeField()
    tags = serializers.ListField(child=serializers.CharField(max_length=50))
    reading_time = serializers.IntegerField()
    views = serializers.IntegerField()
    author = serializers.CharField(max_length=100)
    featured_image = serializers.CharField()
