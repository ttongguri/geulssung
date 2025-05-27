from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.nickname

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='follower_set', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # 중복 팔로우 방지

    def __str__(self):
        return f"{self.follower} → {self.following}"