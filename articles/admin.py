from django.contrib import admin
from .models import Article, Category, Tag

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'category', 'created_at')
    list_filter = ('status', 'category', 'tags', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ('category', 'tags')
    date_hierarchy = 'created_at'
    list_display_links = ('title',)
    readonly_fields = ('views', 'likes', 'created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'slug', 'author', 'status', 'category', 'tags', 'image', 'is_top')
        }),
        ('内容', {
            'fields': ('content', 'excerpt')
        }),
        ('统计与时间', {
            'fields': ('views', 'likes', 'created_at', 'updated_at')
        }),
    )

    class Media:
        css = {
            'all': ('css/admin_custom.css','css/admin_tags_chips.css', 'css/base.css')
        }
        js = ('js/admin_jquery_bridge.js','js/admin_select2_init.js',)
