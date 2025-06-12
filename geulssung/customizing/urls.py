from django.urls import path
from .views import user_owned_items_view, store_view, purchase_item, toggle_equip_item, render_character_partial, preview_character
from . import views

urlpatterns = [
    path('my-items/', user_owned_items_view, name='user_owned_items'),
    path('toggle-equip/<int:item_id>/', toggle_equip_item, name='toggle_equip_item'),
    path('store/', store_view, name='store'),
    path('purchase-item/', purchase_item, name='purchase_item'), 
    path('render-character/<int:character_id>/', render_character_partial, name='render_character'),
    path('preview-character/<int:character_id>/', views.preview_character, name='preview_character'),
]