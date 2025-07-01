import os
import sys
import importlib
import django
import pandas as pd
from django.apps import apps
from django.conf import settings

# 1. Django 환경 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geulssung.settings')
django.setup()

# 2. 테이블ID 매핑용
model_table_ids = {}
table_id_counter = 1

# 3. 명세서 데이터 수집
rows = []
row_number = 1
for model in apps.get_models():
    table_name = model._meta.db_table
    if table_name not in model_table_ids:
        model_table_ids[table_name] = table_id_counter
        table_id_counter += 1
    table_id = model_table_ids[table_name]
    table_verbose = model._meta.verbose_name.title() if hasattr(model._meta, 'verbose_name') else table_name
    for idx, field in enumerate(model._meta.get_fields(), start=1):
        # 필드 타입 및 길이
        if hasattr(field, 'max_length') and field.max_length:
            type_str = f"{field.get_internal_type()}({field.max_length})"
        else:
            type_str = field.get_internal_type()
        # PK/FK/-
        if getattr(field, 'primary_key', False):
            key_type = 'PK'
        elif field.is_relation and field.many_to_one:
            key_type = 'FK'
        elif field.is_relation and field.many_to_many:
            key_type = 'FK'
        else:
            key_type = '-'
        # NULL 허용
        null_allowed = getattr(field, 'null', False)
        null_str = 'Y' if null_allowed else 'N'
        # 기본값
        default_str = ''
        if hasattr(field, 'has_default') and field.has_default():
            default = field.default
            if default is not None and not callable(default):
                default_str = default
            else:
                default_str = ''
        # 컬럼명
        col_name = field.name
        # 컬럼 설명
        col_verbose = getattr(field, 'verbose_name', '')
        rows.append({
            '번호': row_number,
            '테이블ID': table_id,
            '테이블명': table_name,
            '테이블설명': table_verbose,
            '컬럼명': col_name,
            '컬럼ID': idx,
            '타입 및 길이': type_str,
            'PK/FK/-': key_type,
            'NULL 허용': null_str,
            '기본값': default_str,
        })
        row_number += 1

# 4. DataFrame 생성 및 엑셀로 저장
df = pd.DataFrame(rows)
df = df[['번호', '테이블ID', '테이블명', '테이블설명', '컬럼명', '컬럼ID', '타입 및 길이', 'PK/FK/-', 'NULL 허용', '기본값']]
df.to_excel('db_schema.xlsx', index=False)
print('db_schema.xlsx 파일이 생성되었습니다.') 