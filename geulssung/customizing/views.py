from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import UserItem, Character, Item

# 캐릭터 소유 아이템 확인
@login_required
def user_owned_items_view(request):
    owned_items = (
        UserItem.objects
        .filter(user=request.user, owned=True)
        .select_related('item', 'item__character')
        .order_by('item__character__name', 'item__part_code')
    )
    equipped_items = owned_items.filter(equipped=True)
    
    return render(request, 'customizing/user_owned_items.html', {
        'owned_items': owned_items,
        'equipped_items': equipped_items,
    })

# 아이템 장착 / 해제 토글
@login_required
def toggle_equip_item(request, item_id):
    if request.method == 'POST':
        # 현재 유저가 소유한 해당 아이템 가져오기
        user_item = get_object_or_404(UserItem, user=request.user, item_id=item_id, owned=True)

        if user_item.equipped:
            # 이미 착용 중이라면 → 해제
            user_item.equipped = False
            user_item.save()
        else:
            # 착용하려는 경우, 같은 part_code의 다른 아이템 해제
            part_code = user_item.item.part_code
            UserItem.objects.filter(
                user=request.user,
                item__part_code=part_code,
                equipped=True
            ).update(equipped=False)

            # 현재 아이템 착용
            user_item.equipped = True
            user_item.save()

            

        return JsonResponse({'success': True, 'equipped': user_item.equipped, 'image_path': user_item.item.image_path,})
    else:
        return JsonResponse({'error': 'POST 요청만 허용됨'}, status=405)


# 상점 페이지 보기
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

