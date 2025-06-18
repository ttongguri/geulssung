from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# 사용자(회원) 모델: 닉네임 필드 추가
class CustomUser(AbstractUser):
    username = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=False, null=True, blank=True)
    nickname = models.CharField(max_length=30, null=True, blank=True, unique=True)
    credit = models.PositiveIntegerField(default=50)

    def __str__(self):
        return self.nickname or self.username or self.email or f"User({self.pk})"

# 팔로우 관계 모델: 팔로워-팔로잉 관계 및 생성일 저장
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