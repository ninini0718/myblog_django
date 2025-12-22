from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse,HttpResponse,FileResponse
from .models import Article, Category, Tag
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
    
    context = {
        'article': article,
        'comments': comments,
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
