from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'nickname', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('추가 필드', {'fields': ('nickname',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)