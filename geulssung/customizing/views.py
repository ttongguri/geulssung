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
    로그인된 사용자가 상점(store.html)을 볼 수 있도록 렌더링합니다.
    """
    return render(request, 'customizing/store.html')