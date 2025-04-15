# admin.py
from django.utils.translation import gettext_lazy as _

from django.contrib import admin
from .models import Company, CompanyConnection

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'industry', 'created_at')
    search_fields = ('name', 'email', 'phone', 'address')
    readonly_fields = ('invitation_code', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'industry', 'description', 'logo')
        }),
        (_('Contact Info'), {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        (_('Meta'), {
            'fields': ('invitation_code', 'is_active', 'created_at', 'updated_at')
        }),
    )

@admin.register(CompanyConnection)
class CompanyConnectionAdmin(admin.ModelAdmin):
    list_display = ('company_from', 'company_to', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = (
        'company_from__name',
        'company_to__name',
    )
    autocomplete_fields = ['company_from', 'company_to']
