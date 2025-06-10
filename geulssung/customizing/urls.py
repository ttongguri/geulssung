from django.urls import path
from .views import user_owned_items_view, store_view, purchase_item

urlpatterns = [
    path('my-items/', user_owned_items_view, name='user_owned_items'),
    path('store/', store_view, name='store'),
    path('purchase-item/', purchase_item, name='purchase_item'), 
]