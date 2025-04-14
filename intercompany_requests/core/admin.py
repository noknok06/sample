from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Company, Request, Comment, Attachment, Activity

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'company', 'role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'company')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('個人情報', {'fields': ('first_name', 'last_name', 'email')}),
        ('所属', {'fields': ('company', 'role')}),
        ('権限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要な日付', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('個人情報', {'fields': ('first_name', 'last_name', 'email')}),
        ('所属', {'fields': ('company', 'role')}),
    )
    ordering = ('username',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'email', 'status', 'created_at', 'active_requests')
    list_filter = ('status', 'industry')
    search_fields = ('name', 'email', 'address')
    ordering = ('name',)

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender_company', 'receiver_company', 'requester', 'status', 'priority', 'created_at', 'due_date')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'sender_company__name', 'receiver_company__name', 'requester__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AttachmentInline, CommentInline]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'request', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'request__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'コメント'

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'request', 'uploaded_by', 'size_display', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('name', 'request__title', 'uploaded_by__username')
    readonly_fields = ('uploaded_at', 'size')
    ordering = ('-uploaded_at',)
    
    def size_display(self, obj):
        # サイズをKB/MB単位で表示
        if obj.size < 1024:
            return f"{obj.size} バイト"
        elif obj.size < 1024 * 1024:
            return f"{obj.size / 1024:.1f} KB"
        else:
            return f"{obj.size / (1024 * 1024):.1f} MB"
    size_display.short_description = 'ファイルサイズ'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'request', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('action', 'user__username', 'request__title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)