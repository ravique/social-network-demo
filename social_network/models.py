from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Base(models.Model):
    created = models.DateTimeField(default=now, blank=False, verbose_name='Created')

    class Meta:
        abstract = True


class Post(Base):
    title = models.CharField(max_length=255, blank=False)
    content = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name='User')


class Like(Base):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='likes', verbose_name='User')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False, related_name='likes', verbose_name='Post')
