from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.http import JsonResponse,HttpResponse,FileResponse
from .models import Article, Category, Tag
from django.core.cache import cache
from .forms import ArticleForm
import markdown
import qrcode
from io import BytesIO
import os
import time
from django.conf import settings
from PIL import Image

def article_list(request):
    """文章列表"""
    articles = Article.objects.filter(status='published')
    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    sort = request.GET.get('sort')  # 排序字段

    # 搜索功能
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )
    
    # 分类筛选
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=category)
    
    # 标签筛选
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        articles = articles.filter(tags=tag)
    
    # 排序
    if sort == 'views':
        articles = articles.order_by('-views', '-created_at')
    elif sort == 'likes':
        articles = articles.order_by('-likes', '-created_at')
    else:
        articles = articles.order_by('-is_top', '-created_at')  # 默认按置顶+时间
    
    # 分页
    paginator = Paginator(articles, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取所有分类和标签
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    # 为每篇文章标记关注/粉丝状态（当前用户）
    current_user = request.user
    if current_user.is_authenticated:
        # 获取当前用户的关注列表和粉丝列表
        following_ids = set(current_user.following.values_list('id', flat=True))
        followers_ids = set(current_user.followers.values_list('id', flat=True))
        
        for article in page_obj:
            article.is_following_author = article.author.id in following_ids
            article.is_follower_of_author = article.author.id in followers_ids
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'query': query,
        'category_slug': category_slug,
        'tag_slug': tag_slug,
        'sort': sort,
    }
    return render(request, 'articles/article_list.html', context)

def article_detail(request, slug):
    """文章详情"""
    article = get_object_or_404(Article, slug=slug)
    
    # 增加浏览量
    article.increase_views()
    
    # 渲染 markdown 内容
    article.content_html = markdown.markdown(
        article.content,
        extensions=["extra", "codehilite", "toc"]
    )

    # 获取父评论
    comments = article.comments.filter(is_approved=True, parent__isnull=True).order_by('created_at')
    
    # 当前用户是否已关注文章作者（用于显示关注按钮）
    is_following_author = False
    is_follower_author = False
    following_ids = set()
    followers_ids = set()
    
    if request.user.is_authenticated:
        try:
            is_following_author = request.user.following.filter(pk=article.author.pk).exists()
            is_follower_author = request.user.followers.filter(pk=article.author.pk).exists()
            # 获取当前用户的关注列表和粉丝列表
            following_ids = set(request.user.following.values_list('id', flat=True))
            followers_ids = set(request.user.followers.values_list('id', flat=True))
        except Exception:
            is_following_author = False
    
    # 为每个评论标记关注/粉丝状态
    for comment in comments:
        comment.is_following_author = comment.author.id in following_ids
        comment.is_follower_of_author = comment.author.id in followers_ids
        # 为回复也标记状态
        for reply in comment.replies.all():
            reply.is_following_author = reply.author.id in following_ids
            reply.is_follower_of_author = reply.author.id in followers_ids

    context = {
        'article': article,
        'comments': comments,
        'is_following_author': is_following_author,
        'is_follower_author': is_follower_author,
    }
    return render(request, 'articles/article_detail.html', context)

@login_required
def create_article(request):
    """创建文章"""
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = request.POST.get('status', 'draft')  # 获取状态
            article.save()
            form.save_m2m()  # 保存多对多关系
            messages.success(request, '文章创建成功！')
            return redirect('articles:article_detail', slug=article.slug)
    else:
        form = ArticleForm()
    
    return render(request, 'articles/create_article.html', {'form': form})

@login_required
def edit_article(request, slug):
    """编辑文章"""
    article = get_object_or_404(Article, slug=slug)
    
    if article.author != request.user and not request.user.is_superuser:
        messages.error(request, '你没有权限编辑此文章')
        return redirect('articles:article_detail', slug=slug)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, '文章更新成功！')
            return redirect('articles:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'articles/edit_article.html', {'form': form, 'article': article})

@login_required
def delete_article(request, slug):
    """删除文章"""
    article = get_object_or_404(Article, slug=slug)
    
    if article.author != request.user and not request.user.is_superuser:
        messages.error(request, '你没有权限删除此文章')
        return redirect('articles:article_detail', slug=slug)
    
    article.delete()
    messages.success(request, '文章删除成功！')
    return redirect('articles:article_list')

@login_required
@require_POST
def like_article(request, slug):
    """点赞文章"""
    article = get_object_or_404(Article, slug=slug)
    article.likes += 1
    article.save(update_fields=['likes'])
    return JsonResponse({'likes': article.likes})

QR_EXPIRE_SECONDS = 3600  # 1小时

def article_qrcode(request, slug):
    article = get_object_or_404(Article, slug=slug)
    qr_dir = os.path.join(settings.MEDIA_ROOT, "qrcodes")
    os.makedirs(qr_dir, exist_ok=True)
    qr_filename = f"article-{article.slug}.png"
    qr_path = os.path.join(qr_dir, qr_filename)

    # 判断是否需要重新生成二维码
    if not os.path.exists(qr_path) or (time.time() - os.path.getmtime(qr_path)) > QR_EXPIRE_SECONDS:
        url = request.build_absolute_uri(article.get_absolute_url())
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # 加 logo
        logo_path = os.path.join(settings.MEDIA_ROOT, "logo.png")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            qr_w, qr_h = qr_img.size
            logo_size = qr_w // 4
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            pos = ((qr_w - logo_size) // 2, (qr_h - logo_size) // 2)
            if logo.mode in ("RGBA", "LA"):
                qr_img.paste(logo, pos, mask=logo)
            else:
                qr_img.paste(logo, pos)

        qr_img.save(qr_path)

    return FileResponse(open(qr_path, "rb"), content_type="image/png")


@login_required
@require_POST
def api_create_tag(request):
    """通过 AJAX 创建新的 Tag（仅限 staff/superuser）"""
    # 允许普通用户创建，但进行速率限制以防滥用
    # 基于用户 id 或 IP 做限流
    if request.user.is_authenticated:
        key = f'tag_create_uid_{request.user.id}'
    else:
        ip = request.META.get('REMOTE_ADDR', 'anon')
        key = f'tag_create_ip_{ip}'

    limit = 5  # 每分钟最多 5 次
    current = cache.get(key) or 0
    if current >= limit:
        return JsonResponse({'success': False, 'message': '创建过于频繁，请稍后再试'}, status=429)
    cache.set(key, current + 1, timeout=60)

    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'message': '标签名不能为空'}, status=400)

    tag, created = Tag.objects.get_or_create(name=name)
    return JsonResponse({'success': True, 'created': created, 'id': tag.id, 'name': tag.name})


@require_GET
def api_search_categories(request):
    q = request.GET.get('q', '').strip()
    if not q:
        qs = Category.objects.all()[:20]
    else:
        qs = Category.objects.filter(name__icontains=q)[:20]
    results = [{'id': c.id, 'name': c.name} for c in qs]
    return JsonResponse({'results': results})


@require_GET
def api_search_tags(request):
    q = request.GET.get('q', '').strip()
    if not q:
        qs = Tag.objects.all()[:50]
    else:
        qs = Tag.objects.filter(name__icontains=q)[:50]
    results = [{'id': t.id, 'name': t.name} for t in qs]
    return JsonResponse({'results': results})
