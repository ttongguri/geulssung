import csv
from customizing.models import Item, Character
csv_path = 'geulssung/data/character_items.csv'  # ← 수정된 경로!
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            character = Character.objects.get(id=int(row['character_id']))
            Item.objects.create(
                character=character,
                part_code=int(row['part_code']),
                name=row['name'],
                image_path=row['image_path'],
                credit=int(row['credit'])
            )
            print(f":흰색_확인_표시: Item 생성 완료: {character.name} - {row['name']}")
        except Character.DoesNotExist:
            print(f":x: Character id {row['character_id']} 없음 → Item 생성 건너뜀")