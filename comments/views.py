from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from articles.models import Article
from .models import Comment
from .forms import CommentForm
from core.utils import contains_sensitive_words
from django.contrib.auth.decorators import user_passes_test

@login_required
def add_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method != 'POST':
        return redirect('articles:article_detail', slug=article.slug)

    form = CommentForm(request.POST, request.FILES)
    if not form.is_valid():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': '表单验证失败'}, status=400)
        messages.error(request, '评论发布失败，请检查表单')
        return redirect('articles:article_detail', slug=article.slug)

    comment = form.save(commit=False)
    comment.article = article
    comment.author = request.user

    # 敏感词过滤
    if contains_sensitive_words(comment.content):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': '评论包含敏感词'}, status=400)
        messages.error(request, '评论包含敏感词，请修改后重试')
        return redirect('articles:article_detail', slug=article.slug)

    parent_id = request.POST.get('parent_id')
    if parent_id:
        try:
            parent_comment = Comment.objects.get(id=parent_id, article=article)
            comment.parent = parent_comment
        except Comment.DoesNotExist:
            comment.parent = None

    comment.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        avatar_url = getattr(comment.author, 'avatar', None)
        avatar_url = avatar_url.url if avatar_url else '/static/images/default-avatar.png'
        image_url = comment.image.url if getattr(comment, 'image', None) else ''
        return JsonResponse({
            'id': comment.id,
            'article_id': article.id,
            'author': getattr(comment.author, 'nickname', None) or comment.author.username,
            'is_author': request.user == comment.author,
            'is_staff': request.user.is_staff,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'likes_count': comment.likes,
            'avatar': avatar_url,
            'image': image_url,
            'is_reply': bool(comment.parent),
            'parent_id': comment.parent.id if comment.parent else None,
            'csrf': request.COOKIES.get('csrftoken'),
        })

    messages.success(request, '评论发布成功！')
    return redirect('articles:article_detail', slug=article.slug)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user and not request.user.is_superuser:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': '无权限'}, status=403)
        messages.error(request, '你没有权限删除此评论')
        return redirect('articles:article_detail', slug=comment.article.slug)

    comment.delete()

    # ✅ AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, '评论删除成功！')
    return redirect('articles:article_detail', slug=comment.article.slug)


@login_required
def like_comment(request, comment_id):
    """点赞评论"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.likes += 1
    comment.save(update_fields=['likes'])
    return JsonResponse({'likes': comment.likes})

@user_passes_test(lambda u: u.is_staff)
def comment_approve(request, comment_id):
    """批准评论"""
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = True
    comment.save(update_fields=['is_approved'])
    messages.success(request=request,message='评论已批准')
    return redirect('articles:article_detail', slug=comment.article.slug)    