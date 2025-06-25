from django.db import models
from django.conf import settings

class SentimentAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    result_text = models.TextField()
    
    def __str__(self):
        return f"{self.user.nickname or self.user.username} - {self.analyzed_at.strftime('%Y-%m-%d')}"

class PostSentiment(models.Model):
    post = models.OneToOneField('post.Post', on_delete=models.CASCADE)
    score = models.IntegerField()  # -1 = 부정, 0 = 중립, 1 = 긍정
    result_text = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)
