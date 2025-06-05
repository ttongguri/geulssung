from django.contrib import admin
from .models import Character, Item, UserItem

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'base_image']
    search_fields = ['name']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'character', 'part_code', 'name', 'image_path']
    list_filter = ['character', 'part_code']
    search_fields = ['name']

@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'item', 'owned', 'equipped']
    list_filter = ['owned', 'equipped', 'item__character']
    search_fields = ['user__nickname', 'item__name']
