import os
import django
import csv
from datetime import datetime
from django.utils.timezone import make_aware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geulssung.settings')  # ✅ 경로 확인
django.setup()

from django.contrib.auth import get_user_model
from prompts.models import GeneratedPrompt
from post.models import Post  # 또는 models.py 경로에 맞게 import

User = get_user_model()

with open('geulssung/data/posts.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        user = User.objects.get(id=int(row['author_id']))

        prompt = None
        if row['prompt_id']:
            try:
                prompt = GeneratedPrompt.objects.get(id=int(row['prompt_id']))
            except GeneratedPrompt.DoesNotExist:
                print(f"❌ prompt_id {row['prompt_id']} not found")

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
            created_at=make_aware(datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S"))
        )
        post.save()
        print(f"✅ Post '{post.title}' saved.")
