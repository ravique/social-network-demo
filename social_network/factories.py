import factory
from django.contrib.auth.models import User

from social_network.models import Post, Like


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('word')
    password = factory.PostGenerationMethodCall('set_password', 32768)


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker('word')
    content = factory.Faker('text')


class LikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Like
