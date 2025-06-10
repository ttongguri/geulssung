from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import UserItem


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

