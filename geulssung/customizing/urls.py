from django.urls import path
from .views import user_owned_items_view, toggle_equip_item

urlpatterns = [
    path('my-items/', user_owned_items_view, name='user_owned_items'),
    path('toggle-equip/<int:item_id>/', toggle_equip_item, name='toggle_equip_item'),
]