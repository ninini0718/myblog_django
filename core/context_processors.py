# core/context_processors.py
from .models import BlogSettings

def blog_settings(request):
    """
    向所有模板的上下文中注入博客全局设置。
    """
    settings = BlogSettings.load()  # 使用我们定义的 load 方法
    return {
        'active_theme': settings.active_theme,
        'site_title': settings.site_title,
        'site_description': settings.site_description,
        'background_image': settings.background_image,
    }
