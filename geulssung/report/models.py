from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class SentimentAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    result_text = models.TextField()
    
    def __str__(self):
        return f"{self.user.nickname or self.user.username} - {self.analyzed_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-analyzed_at']

# class PostSentiment(models.Model):
#     post = models.OneToOneField('post.Post', on_delete=models.CASCADE)
#     score = models.IntegerField()  # -1 = 부정, 0 = 중립, 1 = 긍정
#     result_text = models.TextField()
#     analyzed_at = models.DateTimeField(auto_now_add=True)

class UserLevel(models.Model):
    """사용자 등급 관리 모델"""
    GRADE_CHOICES = [
        ('송사리 (3-4cm)', '송사리 (3-4cm)'),
        ('전어 (20-25cm)', '전어 (20-25cm)'),
        ('도미 (40-60cm)', '도미 (40-60cm)'),
        ('참치 (100-250cm)', '참치 (100-250cm)'),
        ('고래 (15-30m)', '고래 (15-30m)'),
    ]
    
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, unique=True)
    min_posts = models.IntegerField(help_text="이 등급이 되기 위한 최소 발행글 수")
    max_posts = models.IntegerField(help_text="이 등급의 최대 발행글 수 (다음 등급 전까지)", null=True, blank=True)
    image_path = models.CharField(max_length=100, help_text="등급별 이미지 경로")
    description = models.TextField(blank=True, help_text="등급에 대한 설명")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['min_posts']
    
    def __str__(self):
        return f"{self.grade} ({self.min_posts}~{self.max_posts or '∞'}글)"
    
    @classmethod
    def get_user_grade(cls, published_count):
        """발행글 수에 따라 사용자 등급을 반환"""
        try:
            level = cls.objects.filter(min_posts__lte=published_count).order_by('-min_posts').first()
            if level and (level.max_posts is None or published_count <= level.max_posts):
                return level.grade
            return cls.objects.first().grade if cls.objects.exists() else "송사리 (3-4cm)"
        except:
            return "송사리 (3-4cm)"
    
    @classmethod
    def get_user_image_path(cls, published_count):
        """발행글 수에 따라 사용자 등급 이미지 경로를 반환"""
        try:
            level = cls.objects.filter(min_posts__lte=published_count).order_by('-min_posts').first()
            if level and (level.max_posts is None or published_count <= level.max_posts):
                return level.image_path
            return cls.objects.first().image_path if cls.objects.exists() else "/static/images/level/송사리.jpg"
        except:
            return "/static/images/level/송사리.jpg"

