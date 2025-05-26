from django.db import models

class Issue(models.Model):
    CATEGORY_CHOICES = [
        ("정치", "정치"),
        ("경제", "경제"),
        ("사회", "사회"),
        ("문화", "문화"),
        ("국제", "국제"),
        ("지역", "지역"),
        ("스포츠", "스포츠"),
        ("IT과학", "IT과학"),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category}] {self.title}"


class GeneratedPrompt(models.Model):
    GENRE_CHOICES = [
        ("칼럼", "칼럼"),
        ("분석글", "분석글"),
        ("에세이", "에세이"),
        ("시", "시"),
    ]
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="prompts")
    style = models.CharField(max_length=10, choices=GENRE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.issue.title} - {self.style}"
