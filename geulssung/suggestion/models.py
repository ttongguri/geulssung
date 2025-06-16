# suggestion/models.py

from django.db import models
from accounts.models import CustomUser

class Suggestion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"(익명) {self.content[:20]}"
