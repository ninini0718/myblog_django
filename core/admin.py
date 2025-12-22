# core/admin.py
from django.contrib import admin
from .models import BlogSettings

@admin.register(BlogSettings)
class BlogSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'active_theme')
    
    # 因为我们只希望有一条记录，所以禁用添加按钮
    def has_add_permission(self, request):
        # 检查是否已存在一条记录，如果存在，则不显示“增加”按钮
        return not BlogSettings.objects.exists()

