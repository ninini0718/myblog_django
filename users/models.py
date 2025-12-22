from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


# =========================
# User 模型
# =========================
class User(AbstractUser):
    """自定义用户模型"""

    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name='个人简介')
    location = models.CharField(max_length=30, blank=True, null=True, verbose_name='所在地')
    birth_date = models.DateField(null=True, blank=True, verbose_name='生日')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name='个人网站')
    github = models.CharField(max_length=39, blank=True, null=True, verbose_name='GitHub用户名')
    twitter = models.CharField(max_length=15, blank=True, null=True, verbose_name='Twitter用户名')

    # 🔧 关注系统（保留）
    following = models.ManyToManyField(
        'self',
        related_name='followers',
        symmetrical=False,
        blank=True,
        verbose_name='关注'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    # ===== 统计属性 =====
    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    @property
    def articles_count(self):
        """
        前提：
        Article.author = ForeignKey(settings.AUTH_USER_MODEL, related_name='articles')
        """
        return self.articles.count()


# =========================
# UserProfile
# =========================
class UserProfile(models.Model):
    """扩展用户个人资料"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # ===== 个人信息 =====
    nickname = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # ===== 博客个性化 =====
    blog_title = models.CharField(max_length=100, blank=True)
    blog_description = models.TextField(blank=True)

    BLOG_THEME_CHOICES = [
        ('light', '简洁亮色'),
        ('dark', '暗黑模式'),
        ('card', '卡片风格'),
    ]
    blog_theme = models.CharField(
        max_length=20,
        choices=BLOG_THEME_CHOICES,
        default='light'
    )

    blog_background = models.ImageField(
        upload_to='blog_backgrounds/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nickname or self.user.username
