# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import UserItem, Character, Item

# 내 아이템 목록 보기 (사용 중)
@login_required
def user_owned_items_view(request):
    owned_items = (
        UserItem.objects
        .filter(user=request.user, owned=True)
        .select_related('item__character')
        .order_by('item__character__name', 'item__part_code')
    )
    return render(
        request,
        'customizing/user_owned_items.html',
        {'owned_items': owned_items},
    )

# 상점 페이지 보기 (사용 중)
@login_required
def store_view(request):
    owned_item_ids = (
        UserItem.objects
        .filter(user=request.user, owned=True)
        .values_list('item_id', flat=True)
    )
    characters = Character.objects.all().order_by('name')
    all_items = (
        Item.objects
        .select_related('character')
        .all()
        .order_by('character__name', 'part_code')
    )

    return render(
        request,
        'customizing/store.html',
        {
            'characters': characters,
            'all_items': all_items,
            'owned_item_ids': set(owned_item_ids),
        },
    )

# 구매 처리 (사용 중)
@require_POST
@login_required
def purchase_item(request):
    item_id = request.POST.get('item_id')
    item = get_object_or_404(Item, id=item_id)
    user = request.user

    # 이미 보유했는지 검사
    if UserItem.objects.filter(user=user, item=item).exists():
        return JsonResponse({'success': False, 'error': 'already_owned'})

    # 크레딧 충분한지 검사
    if user.credit < item.credit:
        return JsonResponse({'success': False, 'error': 'not_enough_credit'})

    # 크레딧 차감
    user.credit -= item.credit
    user.save()

    # UserItem 생성 (owned=True 명시)
    UserItem.objects.create(user=user, item=item, owned=True)

    return JsonResponse({'success': True})

# TODO: 앞으로 환불 취소 로직이 필요하면 아래에 추가
