from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from core.email_manager import email_manager
from django.core.mail import EmailMessage
from decouple import config
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from users.models import User, UserProfile
from articles.models import Article
from comments.models import Comment
from .models import BlogSettings
from django.views.decorators.http import require_POST

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def test_email_providers(request):
    """测试所有邮件提供商"""
    if request.method == 'POST':
        results = email_manager.test_all_providers()
        return JsonResponse({'results': results})
    
    return render(request, 'core/test_email.html')

@login_required
def send_test_email(request):
    """发送测试邮件"""
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        provider = request.POST.get('provider', 'AUTO')
        
        message = EmailMessage(
            subject='测试邮件',
            body='这是一封测试邮件，用于验证邮件系统是否正常工作。',
            from_email=config('DEFAULT_FROM_EMAIL'),
            to=[recipient],
        )
        
        try:
            if provider == 'AUTO':
                success = email_manager.send_email_with_fallback(message)
            else:
                connection = email_manager.get_connection(provider)
                result = connection.send_messages([message])
                success = result > 0
            
            if success:
                messages.success(request, f'邮件发送成功！使用提供商: {provider}')
            else:
                messages.error(request, '邮件发送失败')
        except Exception as e:
            messages.error(request, f'邮件发送失败: {str(e)}')
        
        return redirect('core:test_email')
    
    return render(request, 'core/send_test_email.html')


@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    users_count = User.objects.count()
    articles_count = Article.objects.count()
    comments_count = Comment.objects.count()
    settings_obj = BlogSettings.load()
    return render(request, 'core/admin_dashboard.html', {
        'users_count': users_count,
        'articles_count': articles_count,
        'comments_count': comments_count,
        'settings': settings_obj,
    })


@login_required
@user_passes_test(is_superuser)
def admin_users(request):
    qs = User.objects.all().order_by('-date_joined')
    paginator = Paginator(qs, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'core/admin_users.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_superuser)
@require_POST
def admin_user_action(request, user_id):
    action = request.POST.get('action')
    user = get_object_or_404(User, id=user_id)
    if action == 'ban':
        user.is_active = False
        user.save(update_fields=['is_active'])
        return JsonResponse({'success': True, 'message': '用户已封禁'})
    elif action == 'unban':
        user.is_active = True
        user.save(update_fields=['is_active'])
        return JsonResponse({'success': True, 'message': '用户已解封'})
    elif action == 'delete':
        user.delete()
        return JsonResponse({'success': True, 'message': '用户已删除'})
    return JsonResponse({'success': False, 'message': '未知操作'}, status=400)


@login_required
@user_passes_test(is_superuser)
def admin_articles(request):
    qs = Article.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'core/admin_articles.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_superuser)
def admin_edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.title = request.POST.get('title', article.title)
        article.content = request.POST.get('content', article.content)
        article.status = request.POST.get('status', article.status)
        article.save()
        messages.success(request, '文章已更新')
        return redirect('core:admin_articles')
    return render(request, 'core/admin_edit_article.html', {'article': article})


@login_required
@user_passes_test(is_superuser)
@require_POST
def admin_delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    article.delete()
    return JsonResponse({'success': True})


@login_required
@user_passes_test(is_superuser)
def admin_comments(request):
    qs = Comment.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 20)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'core/admin_comments.html', {'page_obj': page_obj})


@login_required
@user_passes_test(is_superuser)
@require_POST
def admin_delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return JsonResponse({'success': True})


@login_required
@user_passes_test(is_superuser)
def admin_settings(request):
    settings_obj = BlogSettings.load()
    if request.method == 'POST':
        settings_obj.site_title = request.POST.get('site_title', settings_obj.site_title)
        settings_obj.site_description = request.POST.get('site_description', settings_obj.site_description)
        theme = request.POST.get('active_theme', settings_obj.active_theme)
        settings_obj.active_theme = theme
        # 处理背景图片上传
        if request.FILES.get('background_image'):
            settings_obj.background_image = request.FILES.get('background_image')
        settings_obj.save()
        messages.success(request, '系统设置已保存')
        return redirect('core:admin_settings')
    return render(request, 'core/admin_settings.html', {'settings': settings_obj})
