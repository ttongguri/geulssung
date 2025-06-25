import pandas as pd
from post.models import Post
from account.models import User
from datetime import datetime
from django.utils import timezone

# CSV 로드
df = pd.read_csv("geulssung/data/posts.csv")

for _, row in df.iterrows():
    try:
        user = User.objects.get(id=row["author_id"])
    except User.DoesNotExist:
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
        custom_prompt=row.get("custom_prompt", None)
    )

    # created_at 직접 덮어쓰기
    created_at = timezone.make_aware(datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S"))
    Post.objects.filter(id=post.id).update(created_at=created_at)