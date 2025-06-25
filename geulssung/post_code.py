import os
import django
import csv
from datetime import datetime

# Django 셋업
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geulssung.settings')
django.setup()

# 모델 import
from django.contrib.auth import get_user_model
from prompts.models import GeneratedPrompt
from post.models import Post

User = get_user_model()

# CSV 열기
with open('geulssung/data/posts.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # 유저 가져오기
        try:
            user = User.objects.get(id=int(row['author_id']))
        except User.DoesNotExist:
            print(f"❌ User id {row['author_id']} not found")
            continue

        # 글감 연결
        prompt = None
        if row.get('prompt_id'):
            try:
                prompt = GeneratedPrompt.objects.get(id=int(row['prompt_id']))
            except GeneratedPrompt.DoesNotExist:
                print(f"❌ Prompt id {row['prompt_id']} not found")

        # created_at 파싱
        try:
            created_at = datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"❌ created_at 파싱 실패: {row['created_at']} → {e}")
            continue

        # Post 생성
        post = Post(
            author=user,
            title=row['title'],
            category=row['category'],
            genre=row['genre'],
            step1=row['step1'],
            step2=row['step2'],
            step3=row['step3'],
            final_content=row['final_content'],
            prompt=prompt,
            custom_prompt=row['custom_prompt'] or None,
            is_public=row['is_public'].lower() == 'true',
        )
        post.save()

        # created_at 덮어쓰기 (auto_now_add 우회)
        Post.objects.filter(id=post.id).update(created_at=created_at)
        print(f"✅ Post '{post.title}' saved at {created_at}")
