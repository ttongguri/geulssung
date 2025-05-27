from django.db import models
from django.contrib.auth import get_user_model
from prompts.models import GeneratedPrompt
from django.conf import settings


User = get_user_model()

# 게시글 모델
class Post(models.Model):
    GENRE_CHOICES = [
        ('column', '칼럼'),
        ('analysis', '분석글'),
        ('essay', '에세이'),
        ('poem', '시'),
    ]

    CATEGORY_CHOICES = [
        ('T', '논리적 글쓰기'),
        ('F', '감정적 글쓰기'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    step1 = models.TextField(blank=True)
    step2 = models.TextField(blank=True)
    step3 = models.TextField(blank=True)
    final_content = models.TextField()

    prompt = models.ForeignKey(  # 글감과 관계 형성
        GeneratedPrompt,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referenced_posts"
    )

    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 이 글에 좋아요 누른 사람
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='like_posts',
    )

    def __str__(self):
        return f"[{self.get_genre_display()}] {self.title} by {self.author.nickname}"

# 게시글 이미지 모델
class PostImage(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images/')  # media/post_images/ 에 저장
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title}의 표지 이미지"

    