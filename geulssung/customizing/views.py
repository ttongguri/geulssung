from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserItem, Character, Item

# 캐릭터 소유 아이템 확인
@login_required
def user_owned_items_view(request):
    owned_items = (
        UserItem.objects
        .filter(user=request.user, owned=True)
        .select_related('item__character')
        .order_by('item__character__name', 'item__part_code')
    )
    return render(request, 'customizing/user_owned_items.html', {
        'owned_items': owned_items,
    })

# 상점 페이지 뷰
@login_required
def store_view(request):
    """
    로그인된 사용자가 상점(store.html)을 볼 수 있도록,
    ── 1) 전체 캐릭터 정보
    ── 2) 각 캐릭터의 Item 목록
    ── 3) 사용자(현재 로그인한 user)가 이미 보유한 아이템 ID 리스트
    를 템플릿에 넘겨줍니다.
    """
    # 1) 현재 사용자가 보유한 UserItem 중 owned=True인 item_id 목록
    owned_item_ids = (
        UserItem.objects
        .filter(user=request.user, owned=True)
        .values_list('item_id', flat=True)
    )

    # 2) 모든 캐릭터와, 그 캐릭터에 속한 Item 목록 가져오기
    characters = Character.objects.all().order_by('name')
    # 예시: 각 캐릭터마다 Item을 가져올 때는 template에서 item.character로 구분
    # 또는 views에서 미리 묶을 수도 있지만, 여기서는 캐릭터 리스트와 Item 전체를 넘깁니다.
    all_items = Item.objects.select_related('character').all().order_by('character__name', 'part_code')

    return render(request, 'customizing/store.html', {
        'characters': characters,       # 전체 캐릭터
        'all_items': all_items,         # 전체 Item
        'owned_item_ids': set(owned_item_ids),  # 빠른 검색을 위해 set으로 넘김
    })