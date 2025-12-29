# core/context_processors.py
from .models import BlogSettings
from django.contrib.auth import get_user_model

User = get_user_model()

def blog_settings(request):
    """
    向所有模板的上下文中注入博客全局设置。
    """
    settings = BlogSettings.load()  # 使用我们定义的 load 方法
    # 注入未读通知计数，避免模板中进行复杂查询或调用方法
    unread_count = 0
    try:
        if request.user and request.user.is_authenticated:
            unread_count = request.user.notifications.filter(unread=True).count()
    except Exception:
        unread_count = 0
    # 优先使用用户个人主题配置（若存在），否则使用站点主题
    effective_theme = settings.active_theme
    try:
        if request.user and request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile and getattr(profile, 'blog_theme', None):
                effective_theme = profile.blog_theme
    except Exception:
        pass

    return {
        'active_theme': effective_theme,
        'site_title': settings.site_title,
        'site_description': settings.site_description,
        'background_image': settings.background_image,
        'notification_unread_count': unread_count,
    }
