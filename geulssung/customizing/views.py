from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserItem

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

def customize_avatar_view(request):
    top_items = Item.objects.filter(part_code='TOP')  # 필요에 따라 수정
    return render(request, 'customize_avatar.html', {'top_items': top_items})