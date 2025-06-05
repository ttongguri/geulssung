from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# 캐릭터 모델
class Character(models.Model):
    name = models.CharField(max_length=50)  # 캐릭터 이름
    base_image = models.CharField(max_length=255)  # 기본 이미지 경로

    def __str__(self):
        return self.name

# 아이템 부위 모델
class Item(models.Model):
    PART_CHOICES = [
        (1, '몸체'),
        (2, '가방'),
        (3, '안경'),
        (4, '모자'),
        (5, '악세사리'),
        (6, '옷'),
        
        # 필요 시 추가 가능
    ]

    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='items')
    part_code = models.IntegerField(choices=PART_CHOICES)
    name = models.CharField(max_length=100)  # ex: 'body1', 'glass_red'
    image_path = models.CharField(max_length=255)
    credit = models.PositiveIntegerField(default=60)


    def __str__(self):
        return f"{self.character.name} - {self.get_part_code_display()} - {self.name}"

# 유저 아이템 모델
class UserItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    owned = models.BooleanField(default=False)
    equipped = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        status = '착용중' if self.equipped else '보유중' if self.owned else '미보유'
        return f"{self.user.nickname} - {self.item} ({status})"
