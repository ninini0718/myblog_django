from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from articles.models import Article
from .models import Comment
from .forms import CommentForm
from core.utils import contains_sensitive_words
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

@login_required
def add_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method != 'POST':
        return redirect('articles:article_detail', slug=article.slug)

    form = CommentForm(request.POST, request.FILES)
    if not form.is_valid():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': '表单验证失败'}, status=400)
        messages.error(request, '评论发布失败，请检查表单')
        return redirect('articles:article_detail', slug=article.slug)

    comment = form.save(commit=False)
    comment.article = article
    comment.author = request.user

    # 防止重复提交：若在短时间内已有同一用户对同一文章/父评论提交相同内容，则复用已存在的评论
    try:
        recent_threshold = timezone.now() - timedelta(seconds=5)
        existing = Comment.objects.filter(
            article=article,
            author=request.user,
            content=comment.content,
            parent=comment.parent,
            created_at__gte=recent_threshold
        ).order_by('-created_at').first()
        if existing:
            comment = existing
            created_flag = False
        else:
            created_flag = True
    except Exception:
        created_flag = True

    # 敏感词过滤
    if contains_sensitive_words(comment.content):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': '评论包含敏感词'}, status=400)
        messages.error(request, '评论包含敏感词，请修改后重试')
        return redirect('articles:article_detail', slug=article.slug)

    # 处理回复
    parent_id = request.POST.get('parent_id')
    if parent_id:
        try:
            parent_comment = Comment.objects.get(id=parent_id, article=article)
            comment.parent = parent_comment
        except Comment.DoesNotExist:
            comment.parent = None

    if created_flag:
        comment.save()

    # AJAX 请求返回 JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        avatar_url = getattr(comment.author, 'avatar', None)
        avatar_url = avatar_url.url if avatar_url else '/static/images/default_avatar.jpg'
        # 获取作者显示名：优先 user.profile.nickname，再尝试 user.nickname（如存在），最后回退到 username
        display_name = None
        try:
            display_name = getattr(getattr(comment.author, 'profile', None), 'nickname', None)
        except Exception:
            display_name = None
        if not display_name:
            display_name = getattr(comment.author, 'nickname', None) if hasattr(comment.author, 'nickname') else None
        if not display_name:
            display_name = comment.author.username
        image_url = comment.image.url if getattr(comment, 'image', None) else ''
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'article_id': article.id,
                'author_avatar': avatar_url,
                'author_nickname': display_name,
                'author_username': comment.author.username,
                'is_author': request.user == comment.author,
                'is_staff': request.user.is_staff,
                'content': comment.content,
                'content_html': comment.content_html if hasattr(comment, 'content_html') else comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                'likes': comment.likes,
                'is_reply': bool(comment.parent),
                'parent_id': comment.parent.id if comment.parent else None,
            }
        })

    # 普通表单提交
    messages.success(request, '评论发布成功！')
    return redirect('articles:article_detail', slug=article.slug)

@login_required
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': '评论不存在'}, status=404)
        messages.warning(request, '评论不存在或已被删除')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if comment.author != request.user and not request.user.is_superuser:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': '无权限'}, status=403)
        messages.error(request, '你没有权限删除此评论')
        return redirect('articles:article_detail', slug=comment.article.slug)

    comment.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'comment_id': comment_id})

    messages.success(request, '评论删除成功！')
    return redirect('articles:article_detail', slug=comment.article.slug)


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.likes += 1
    comment.save(update_fields=['likes'])

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'comment_id': comment.id, 'likes': comment.likes})

    return redirect(request.META.get('HTTP_REFERER', '/'))


@user_passes_test(lambda u: u.is_staff)
def comment_approve(request, comment_id):
    """批准评论"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = True
    comment.save(update_fields=['is_approved'])
    messages.success(request=request,message='评论已批准')
    return redirect('articles:article_detail', slug=comment.article.slug)    


@login_required
def notifications_json(request):
    """返回当前用户最近的通知（JSON），供前端轮询或下拉使用"""
    qs = request.user.notifications.all()[:20]
    items = []
    for n in qs:
        items.append({
            'id': n.id,
            'actor': getattr(n.actor, 'username', None) if n.actor else None,
            'actor_avatar': (getattr(getattr(n.actor, 'profile', None), 'avatar', None).url if getattr(getattr(n.actor, 'profile', None), 'avatar', None) else (getattr(n.actor, 'avatar', None).url if getattr(n.actor, 'avatar', None) else '/static/images/default_avatar.jpg')) if n.actor else '/static/images/default_avatar.jpg',
            'verb': n.verb,
            'unread': n.unread,
            'timestamp': n.timestamp.strftime('%Y-%m-%d %H:%M'),
            'data': n.data or {},
        })
    return JsonResponse({'notifications': items, 'unread_count': request.user.notifications.filter(unread=True).count()})


@login_required
def mark_notification(request):
    """标记单条通知为已读（或删除），通过 POST 调用"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    nid = request.POST.get('notification_id')
    action = request.POST.get('action', 'mark_read')
    try:
        n = request.user.notifications.get(id=nid)
    except Exception:
        return JsonResponse({'error': '通知不存在'}, status=404)

    if action == 'mark_read':
        n.mark_as_read()
        return JsonResponse({'success': True})
    elif action == 'delete':
        n.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': '未知操作'}, status=400)


def fetch_comment(request, comment_id):
    """AJAX: 返回指定评论的渲染 HTML，用于在文章页面按需加载某条评论（如果分页或懒加载时）"""
    try:
        comment = Comment.objects.select_related('author', 'article', 'parent').get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'error': '评论未找到'}, status=404)

    html = render_to_string('comments/comment_item.html', {
        'comment': comment,
        'user': request.user,
    }, request=request)

    # 计算该评论所在的分页页码（针对父级评论分页）
    try:
        per_page = int(request.GET.get('per_page') or 10)
    except ValueError:
        per_page = 10

    # 如果是回复，则以父评论为定位对象
    target = comment.parent if comment.parent else comment
    # 只统计顶级（parent is null）且已批准的父评论
    qs = Comment.objects.filter(article=target.article, parent__isnull=True, is_approved=True).order_by('created_at')
    # 计算在此序列之前的数量以确定页码
    rank = qs.filter(created_at__lt=target.created_at).count()
    page = rank // per_page + 1

    return JsonResponse({
        'html': html,
        'comment_id': comment.id,
        'article_slug': getattr(comment.article, 'slug', None),
        'page': page,
        'is_reply': bool(comment.parent),
        'parent_id': comment.parent.id if comment.parent else None,
        'created_at': comment.created_at.isoformat(),
    })


@login_required
def notifications_page(request):
    """渲染通知页面，支持分页"""
    qs = request.user.notifications.all()
    paginator = Paginator(qs, 20)
    page_num = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_num)
    return render(request, 'comments/notifications_page.html', {
        'notifications': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })