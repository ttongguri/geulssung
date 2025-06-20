import os
import django

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geulssung.settings')
django.setup()

import csv
from customizing.models import Item, Character

# CSV 파일 경로 지정
csv_path = 'geulssung/data/character_items.csv'

# CSV 파일 열기
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            # 캐릭터 ID로 Character 객체 조회
            character = Character.objects.get(id=int(row['character_id']))

            # ✅ name + character + part_code 조합으로 아이템 검색 후,
            # 있으면 업데이트 / 없으면 새로 생성
            item, created = Item.objects.update_or_create(
                name=row['name'],
                character=character,
                part_code=int(row['part_code']),
                defaults={
                    'image_path': row['image_path'],
                    'credit': int(row['credit']),
                }
            )

            # 생성 여부에 따른 출력 로그
            if created:
                print(f"✅ 생성: {character.name} - {row['name']} (part {row['part_code']})")
            else:
                print(f"🔁 업데이트: {character.name} - {row['name']} (part {row['part_code']})")

        except Character.DoesNotExist:
            # 존재하지 않는 캐릭터일 경우 예외 처리
            print(f"❌ Character id {row['character_id']} 없음 → 건너뜀")
