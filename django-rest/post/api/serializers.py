from rest_framework import serializers
from post.models import Post


class PostSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        #url'e taklayinca nereye gitmek istiyorsam orayi yaziyorum. post'un detayina gitmek istedigim icin:
        #post = namespace (app_name yani) (namespace esas url'de), url'de belirtmeyi unutma!!
        view_name='post:detail',
        lookup_field='slug',
    )

    username = serializers.SerializerMethodField(method_name='username_new')

    class Meta:
        model = Post
        fields = [
            'username',
            'title',
            'url',
            'created',
            'modified_by',
        ]

    def username_new(self, obj):
        return str(obj.user.username)


class PostDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'image',
            'created',
            'modified_by',
        ]
