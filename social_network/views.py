from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenViewBase
from django_filters import rest_framework as filters

from social_network.filters import LikesFilter
from social_network.models import Post, Like
from social_network.serializers import UserSerializer, PostSerializer, LikeSerializer, \
    TokenObtainPairSerializerAndLogin, UserActivitySerializer, AggregatedLikeSerializer, PostListSerializer, \
    PostCreateSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = AllowAny,
    serializer_class = UserSerializer


class LoginView(TokenViewBase):
    serializer_class = TokenObtainPairSerializerAndLogin


class PostView(generics.RetrieveAPIView):
    permission_classes = IsAuthenticated,
    queryset = Post.objects.prefetch_related('likes')
    serializer_class = PostSerializer


class PostListView(generics.ListAPIView, generics.CreateAPIView):
    permission_classes = IsAuthenticated,
    queryset = Post.objects.prefetch_related('likes')
    serializer_class = PostCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, *args, **kwargs):
        serializer_class = PostListSerializer
        serializer = serializer_class(self.get_queryset())
        return Response(serializer.data)


class LikeView(generics.CreateAPIView):
    permission_classes = IsAuthenticated,
    serializer_class = LikeSerializer

    def get_serializer_context(self):
        response = super().get_serializer_context()
        response['request'].data.update({
            'post': self.kwargs.get('post_id'),
            'user': self.request.user.id
        })
        return response


class DislikeView(APIView):
    permission_classes = IsAuthenticated,

    def post(self, request, post_id):
        like = get_object_or_404(Like, user=request.user, post_id=post_id)
        serialized_like = LikeSerializer(like)
        like.delete()
        return Response(serialized_like.data)


class UserActivityView(generics.RetrieveAPIView):
    permission_classes = IsAuthenticated,
    queryset = User.objects.all()
    serializer_class = UserActivitySerializer


class AnalyticsView(generics.ListAPIView):
    permission_classes = IsAuthenticated,

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LikesFilter
    queryset = Like.objects.values('created__date').annotate(total=Count('id'))
    serializer_class = AggregatedLikeSerializer
