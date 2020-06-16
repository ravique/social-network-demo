from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from sn_test_task.redis import redis_instance
from social_network.models import Post, Like


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'username', 'password',
        read_only_fields = 'id',
        extra_kwargs = {'password': {'write_only': True}}

    @staticmethod
    def validate_password(password):
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return password

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = 'id', 'created',


class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField('get_likes_count')
    user = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='sn:user_stats',
        lookup_field='pk'
    )

    @staticmethod
    def get_likes_count(instance):
        return Like.objects.filter(post=instance).count()

    class Meta:
        model = Post
        fields = 'id', 'user', 'title', 'likes_count', 'created', 'content'
        read_only_fields = 'id', 'created',


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = 'id', 'created',


class PostListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = 'id', 'link', 'created', 'title', 'content',
        read_only_fields = 'id', 'created'
        extra_kwargs = {
            'link': {'view_name': 'sn:post_detail', 'lookup_field': 'pk'},
        }


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = 'id', 'created'
        validators = [
            UniqueTogetherValidator(
                queryset=Like.objects.all(),
                fields=['user', 'post'],
                message='You liked this post already. Please, try to like another post.'
            )
        ]


class DislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'


class TokenObtainPairSerializerAndLogin(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        user.last_login = now()
        user.save()
        return super().get_token(user)


class UserActivitySerializer(serializers.ModelSerializer):
    last_request = serializers.SerializerMethodField(source='get_last_request')

    @staticmethod
    def get_last_request(instance):
        user_key = '_'.join(('user', str(instance.id)))
        last_request = redis_instance.get(user_key)
        return last_request

    class Meta:
        model = User
        fields = 'id', 'username', 'last_login', 'last_request'


class AggregatedLikeSerializer(serializers.Serializer):
    created__date = serializers.DateField()
    total = serializers.IntegerField()
