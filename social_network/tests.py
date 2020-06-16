import json

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from social_network.factories import UserFactory, PostFactory, LikeFactory
from social_network.models import Post, Like

client = APIClient()


@pytest.mark.django_db
class TestUser:
    def setup(self):
        UserFactory.create(username='testuser', password='32768')

    def test_RegisterView(self):
        response_from_url = client.post(
            path='/api/user/register/',
            data={
                'username': 'Koala',
                'password': 'notordinarypassword'
            }
        )

        response_dict = json.loads(response_from_url.content)

        assert response_from_url.status_code == 201
        assert "id" in response_dict.keys()
        assert "username" in response_dict.keys()
        assert "password" not in response_dict.keys()

    def test_LoginView(self):
        response_from_url = client.post(
            path='/api/user/login/',
            data={
                'username': 'testuser',
                'password': '32768'
            }
        )

        response_dict = json.loads(response_from_url.content)

        assert response_from_url.status_code == 200
        assert "access" in response_dict.keys()
        assert "refresh" in response_dict.keys()


@pytest.mark.django_db
class TestPostView:
    def setup(self):
        user = UserFactory.create(username='testuser', password='32768')
        self.test_post = PostFactory.create(user=user)
        self.jwt = str(RefreshToken.for_user(user).access_token)

    def teardown(self):
        client.credentials()

    def test_PostView_unauthorized(self):
        response_from_url = client.get(
            path='/api/post/',
        )

        assert response_from_url.status_code == 401

    def test_PostView_list(self):
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.jwt)
        response_from_url = client.get(
            path='/api/post/',
        )

        response_dict = json.loads(response_from_url.content)

        assert response_from_url.status_code == 200
        assert response_dict['count'] == 1
        assert len(response_dict['results']) == 1
        assert response_dict['results'][0]['id'] == self.test_post.id
        assert response_dict['results'][0]['title'] == self.test_post.title
        assert response_dict['results'][0]['content'] == self.test_post.content


@pytest.mark.django_db
class TestPostCreate:
    def setup(self):
        self.user = UserFactory.create(username='testuser', password='32768')
        self.jwt = str(RefreshToken.for_user(self.user).access_token)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.jwt)

    def test_PostCreate(self):
        response_from_url = client.post(
            path='/api/post/',
            data={
                'title': 'title',
                'content': 'content'
            }
        )
        post = Post.objects.first()

        assert response_from_url.status_code == 201
        assert post.title == 'title'
        assert post.content == 'content'
        assert post.user_id == self.user.id


@pytest.mark.django_db
class TestLike:
    def setup(self):
        self.user = UserFactory.create(username='testuser', password='32768')
        self.post = PostFactory.create()
        self.jwt = str(RefreshToken.for_user(self.user).access_token)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.jwt)

    def teardown(self):
        client.credentials()

    def test_Like(self):
        response_from_url = client.post(
            path=f'/api/post/{str(self.post.id)}/like/'
        )
        like = Like.objects.first()

        assert response_from_url.status_code == 201
        assert like.post_id == self.post.id
        assert Like.objects.filter(post_id=self.post.id).count() == 1

    def test_Dislike(self):
        client.post(
            path=f'/api/post/{str(self.post.id)}/like/'
        )
        response_from_url = client.post(
            path=f'/api/post/{str(self.post.id)}/dislike/'
        )

        assert response_from_url.status_code == 200
        assert Like.objects.count() == 0

    def test_DoubleLike(self):
        client.post(
            path=f'/api/post/{str(self.post.id)}/like/'
        )
        response_from_url = client.post(
            path=f'/api/post/{str(self.post.id)}/like/'
        )

        assert response_from_url.status_code == 400

    def test_NotExistedLike(self):
        response_from_url = client.post(
            path=f'/api/post/{str(self.post.id)}/dislike/'
        )
        assert response_from_url.status_code == 404


@pytest.mark.django_db
class TestLikeAnalytics:
    def setup(self):
        self.user = UserFactory.create(username='testuser', password='32768')
        self.jwt = str(RefreshToken.for_user(self.user).access_token)
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.jwt)

        creation_dates = (
            '2010-01-01',
            '2020-01-01',
            '2020-02-01',
            '2020-02-01',
            '2020-02-10'
        )
        posts = PostFactory.create_batch(len(creation_dates))

        posts_and_likes = zip(creation_dates, posts)
        for like_date, post in posts_and_likes:
            LikeFactory.create(post=post, created=like_date)

    def test_AllLikes(self):
        response_from_url = client.get(
            path=f'/api/like/analytics/'
        )

        response_dict = json.loads(response_from_url.content)

        two_likes_day = None
        for day in response_dict['results']:
            if day['total'] == 2:
                two_likes_day = day['created__date']
                break

        assert response_dict['count'] == 4
        assert two_likes_day == '2020-02-01'

    def test_LikesFilter(self):
        response_from_url = client.get(
            path=f'/api/like/analytics/?date_from=2020-01-01&date_to=2020-02-01'
        )

        response_dict = json.loads(response_from_url.content)
        assert response_dict['count'] == 2
        assert {'created__date': '2020-01-01', 'total': 1} in response_dict['results']
        assert {'created__date': '2020-02-01', 'total': 2} in response_dict['results']

