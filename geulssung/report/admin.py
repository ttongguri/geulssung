from django.contrib import admin
from .models import UserLevel, SentimentAnalysis

@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'analyzed_at', 'result_text']
    list_filter = ['analyzed_at']
    search_fields = ['user__nickname', 'user__username']

@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ['grade', 'min_posts', 'max_posts', 'image_path', 'created_at']
    list_filter = ['grade', 'created_at']
    search_fields = ['grade', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('등급 정보', {
            'fields': ('grade', 'min_posts', 'max_posts')
        }),
        ('이미지 설정', {
            'fields': ('image_path',)
        }),
        ('설명', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('시간 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
