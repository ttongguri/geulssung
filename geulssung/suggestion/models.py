# suggestion/models.py

from django.db import models
from accounts.models import CustomUser

class Suggestion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
<<<<<<< HEAD

    def __str__(self):
        return f"(익명) {self.content[:20]}"
=======
    
    upvoted_users = models.ManyToManyField(CustomUser, related_name='upvoted_suggestions', blank=True)
    downvoted_users = models.ManyToManyField(CustomUser, related_name='downvoted_suggestions', blank=True)

    def __str__(self):
        return f"(익명) {self.content[:20]}"
>>>>>>> 5a73aed7ff6a5d0aa3907574986505c02b7c2e24
