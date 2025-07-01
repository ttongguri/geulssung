import os
import django
import pandas as pd
from datetime import datetime
from django.utils import timezone

# Django 환경 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geulssung.settings")
django.setup()

from accounts.models import CustomUser
from post.models import Post

# CSV 로드
df = pd.read_csv("geulssung/geulssung/geulssung/data/posts.csv")

for _, row in df.iterrows():
    try:
        user = CustomUser.objects.get(id=row["author_id"])
    except CustomUser.DoesNotExist:
        continue  # 존재하지 않는 유저는 건너뜀

    post = Post.objects.create(
        author=user,
        title=row["title"],
        category=row["category"],
        genre=row["genre"],
        step1=row["step1"],
        step2=row["step2"],
        step3=row["step3"],
        final_content=row["final_content"],
        is_public=row["is_public"],
        custom_prompt=row["custom_prompt"] if "custom_prompt" in row and not pd.isna(row["custom_prompt"]) else None
    )

    # created_at 직접 덮어쓰기
    created_at = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
    Post.objects.filter(id=post.id).update(created_at=created_at)