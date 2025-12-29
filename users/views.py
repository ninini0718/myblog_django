from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Count
from articles.models import Article
from django.contrib.auth import update_session_auth_hash
from .forms import UserUpdateForm, CustomPasswordChangeForm
from .models import UserProfile
from django.core.paginator import Paginator
from django.contrib.auth import views as auth_views
from django.contrib.contenttypes.models import ContentType
from core.models import Notification
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model

User = get_user_model()

User = get_user_model()

password_reset = auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html')
password_reset_done = auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html')
password_reset_confirm = auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html')
password_reset_complete = auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html')
@login_required
def profile(request):
    """当前登录用户的个人资料页面（整合式，支持分页和排序）"""
    user = request.user
    
    # 1️⃣ 获取排序参数，默认按创建时间倒序
    sort = request.GET.get('sort', 'created_at')
    if sort not in ['created_at', 'views', 'likes']:
        sort = 'created_at'  # 安全处理
    
    # 2️⃣ 根据排序获取文章列表
    if sort == 'created_at':
        articles_qs = Article.objects.filter(author=user, status='published').order_by('-created_at', '-is_top')
    elif sort == 'views':
        articles_qs = Article.objects.filter(author=user, status='published').order_by('-views', '-created_at')
    else:  # sort == 'likes'
        articles_qs = Article.objects.filter(author=user, status='published').order_by('-likes', '-created_at')
    
    # 3️⃣ 分页，每页 5 篇文章
    paginator = Paginator(articles_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 4️⃣ 获取关注和粉丝列表
    following_list = user.following.all()
    followers_list = user.followers.all()
    
    context = {
        'profile_user': user,        # 当前用户
        'articles': page_obj,        # 分页后的文章列表
        'following': following_list,
        'followers': followers_list,
        'is_own_profile': True,      # 标记是自己的页面
        'sort': sort,                # 当前排序方式
    }
    return render(request, 'users/profile.html', context)


def user_profile(request, username):
    """查看其他用户的资料页面（支持分页和排序）"""
    profile_user = get_object_or_404(User, username=username)
    
    # 1️⃣ 获取排序参数
    sort = request.GET.get('sort', 'created_at')
    if sort not in ['created_at', 'views', 'likes']:
        sort = 'created_at'
    
    # 2️⃣ 根据排序获取文章列表
    if sort == 'created_at':
        articles_qs = Article.objects.filter(author=profile_user, status='published').order_by('-created_at', '-is_top')
    elif sort == 'views':
        articles_qs = Article.objects.filter(author=profile_user, status='published').order_by('-views', '-created_at')
    else:  # sort == 'likes'
        articles_qs = Article.objects.filter(author=profile_user, status='published').order_by('-likes', '-created_at')
    
    # 3️⃣ 分页，每页 5 篇文章
    paginator = Paginator(articles_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 4️⃣ 获取关注和粉丝列表
    following_list = profile_user.following.all()
    followers_list = profile_user.followers.all()
    
    # 5️⃣ 判断当前用户是否已关注该用户
    is_following = False
    if request.user.is_authenticated:
        is_following = request.user.following.filter(pk=profile_user.pk).exists()
    
    context = {
        'profile_user': profile_user,
        'articles': page_obj,        # 分页后的文章列表
        'following': following_list,
        'followers': followers_list,
        'is_following': is_following,
        'is_own_profile': False,
        'sort': sort,                # 当前排序方式
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """
    编辑个人资料 + 博客设置
    """

    # ===============================
    # 🔧 修改点 1：确保 UserProfile 存在
    # 如果没有就自动创建（非常关键）
    # ===============================
    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    # ===============================
    # 🔧 修改点 2：Form 绑定的是 profile，而不是 user
    # ===============================
    if request.method == 'POST':
        form = UserUpdateForm(
            request.POST,
            request.FILES,
            instance=profile   # ✅ 关键修复点
        )
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料已更新')
            return redirect('users:profile')
    else:
        form = UserUpdateForm(
            instance=profile   # ✅ 关键修复点
        )

    return render(request, 'users/edit_profile.html', {
        'form': form
    })

def user_articles(request, username):
    """查看指定用户的文章列表（支持分页和排序）"""
    user = get_object_or_404(User, username=username)
    
    # 1️⃣ 获取排序参数，默认按时间倒序
    sort = request.GET.get('sort', 'created_at')
    if sort not in ['created_at', 'views', 'likes']:
        sort = 'created_at'  # 安全处理，防止非法值
    
    # 2️⃣ 根据排序获取文章列表
    if sort == 'created_at':
        articles_qs = Article.objects.filter(author=user, status='published').order_by('-created_at', '-is_top')
    elif sort == 'views':
        articles_qs = Article.objects.filter(author=user, status='published').order_by('-views', '-created_at')
    else:  # sort == 'likes'
        articles_qs = Article.objects.filter(author=user, status='published').order_by('-likes', '-created_at')
    
    # 3️⃣ 分页处理，每页 5 篇文章
    paginator = Paginator(articles_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 4️⃣ 渲染模板
    context = {
        'profile_user': user,
        'articles': page_obj,  # 修改点：传递分页后的对象
        'sort': sort,          # 修改点：保留排序信息，用于模板中选中状态
    }
    return render(request, 'users/user_articles.html', context)

@login_required
def following_list(request):
    """我关注的人列表"""
    following = request.user.following.all()
    return render(request, 'users/following.html', {'following': following})

@login_required
def followers_list(request):
    """关注我的人列表"""
    followers = request.user.followers.all()
    return render(request, 'users/followers.html', {'followers': followers})

@login_required
def follow_user(request, username):
    """关注用户"""
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        request.user.following.add(user_to_follow)
        messages.success(request, f'你已关注 {username}')
        try:
            Notification.objects.create(
                recipient=user_to_follow,
                actor=request.user,
                verb='关注了你',
                target_content_type=ContentType.objects.get_for_model(User),
                target_object_id=request.user.id,
                data={'profile_username': request.user.username}
            )
        except Exception:
            # 不影响关注流程，记录异常到日志由其他地方查看
            pass
    # 修改重定向到用户资料页，而不是文章列表
    return redirect('users:user_profile', username=username)


@login_required
@require_POST
def follow_ajax(request, username):
    """AJAX: 关注用户（返回 JSON）"""
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        return JsonResponse({'success': False, 'message': '不能关注自己'}, status=400)

    already = request.user.following.filter(pk=user_to_follow.pk).exists()
    if already:
        return JsonResponse({'success': False, 'message': '已关注'}, status=400)

    request.user.following.add(user_to_follow)
    try:
        Notification.objects.create(
            recipient=user_to_follow,
            actor=request.user,
            verb='关注了你',
            target_content_type=ContentType.objects.get_for_model(User),
            target_object_id=request.user.id,
            data={'profile_username': request.user.username}
        )
    except Exception:
        pass
    # 返回最新粉丝数，方便前端更新显示
    try:
        followers_count = user_to_follow.followers.count()
    except Exception:
        followers_count = None
    return JsonResponse({'success': True, 'username': username, 'followers_count': followers_count})


@login_required
@require_POST
def unfollow_ajax(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    if user_to_unfollow == request.user:
        return JsonResponse({'success': False, 'message': '不能操作自己'}, status=400)
    request.user.following.remove(user_to_unfollow)
    try:
        followers_count = user_to_unfollow.followers.count()
    except Exception:
        followers_count = None
    return JsonResponse({'success': True, 'username': username, 'followers_count': followers_count})


@login_required
@require_POST
def set_theme(request):
    """设置当前用户的博客主题（AJAX）"""
    theme = request.POST.get('theme')
    if not theme:
        return JsonResponse({'success': False, 'message': '缺少 theme 参数'}, status=400)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.blog_theme = theme
    profile.save(update_fields=['blog_theme'])
    return JsonResponse({'success': True, 'theme': theme})

@login_required
def unfollow_user(request, username):
    """取消关注"""
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.following.remove(user_to_unfollow)
    messages.success(request, f'你已取消关注 {username}')
    # 修改重定向到用户资料页，而不是文章列表
    return redirect('users:user_profile', username=username)

@login_required
def change_password(request):
    """修改密码"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # 保持登录状态
            update_session_auth_hash(request, user)
            messages.success(request, '密码修改成功！')
            return redirect('users:profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'users/change_password.html', {'form': form})