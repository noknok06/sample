from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class CustomUserAdmin(UserAdmin):
    """カスタムユーザーモデルのための管理画面設定"""
    model = User
    list_display = (
        'email', 
        'first_name', 
        'last_name', 
        'company', 
        'role', 
        'is_active', 
        'is_staff'
    )
    list_filter = (
        'is_active', 
        'is_staff', 
        'role', 
        'company'
    )
    search_fields = (
        'email', 
        'first_name', 
        'last_name', 
        'company__name'
    )
    ordering = ('email',)
    
    # フィールドセットのカスタマイズ
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
            'fields': (
                'first_name', 
                'last_name', 
                'position', 
                'phone_number', 
                'profile_picture'
            )
        }),
        (_('Company Info'), {
            'fields': ('company', 'role')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions'
            )
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # ユーザー作成フォームのカスタマイズ
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'password1', 
                'password2', 
                'first_name', 
                'last_name', 
                'company', 
                'role', 
                'is_active', 
                'is_staff'
            )
        }),
    )

# デフォルトのUserAdminを登録解除し、カスタムUserAdminを登録
admin.site.register(User, CustomUserAdmin)