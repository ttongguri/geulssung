from django.contrib import admin
from .models import Issue, GeneratedPrompt

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ["category", "title", "created_at"]
    search_fields = ["title"]

@admin.register(GeneratedPrompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ["issue", "style", "created_at"]
    list_filter = ["style"]
    search_fields = ["content"]
