from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from social_network.views import RegisterView, PostView, LikeView, DislikeView, LoginView, UserActivityView, \
    AnalyticsView, PostListView

app_name = 'sn'

urlpatterns = [
    path('api/user/register/', RegisterView.as_view(), name='user_register'),
    path('api/user/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/user/token_refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/post/', PostListView.as_view(), name='posts_list'),
    path('api/post/<int:pk>/', PostView.as_view(), name='post_detail'),
    path('api/post/<int:post_id>/like/', LikeView.as_view(), name='post_like'),
    path('api/post/<int:post_id>/dislike/', DislikeView.as_view(), name='post_dislike'),

    path('api/user/<int:pk>/', UserActivityView().as_view(), name='user_stats'),
    path('api/like/analytics/', AnalyticsView().as_view(), name='likes')
]
