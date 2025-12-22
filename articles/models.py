from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from django.conf import settings

User = get_user_model()

class Category(models.Model):
    """文章分类"""
    name = models.CharField('分类名', max_length=100, unique=True)
    slug = models.SlugField('URL别名', max_length=100, unique=True, blank=True)
    description = models.TextField('描述', blank=True)
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    """文章标签"""
    name = models.CharField('标签名', max_length=100, unique=True)
    slug = models.SlugField('URL别名', max_length=100, unique=True, blank=True)
    
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Article(models.Model):
    """文章模型"""
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
    )
    
    title = models.CharField('标题', max_length=200)
    slug = models.SlugField('URL别名', max_length=200, unique=True, blank=True) # 确保有 unique=True 和 blank=True
    content = MarkdownxField('内容')  
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles', verbose_name='作者')
    excerpt = models.TextField('摘要', max_length=300, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='draft')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    views = models.PositiveIntegerField('浏览量', default=0)
    likes = models.PositiveIntegerField('点赞数', default=0)
    image = models.ImageField('文章图片', upload_to='article_images/', blank=True)
    is_top = models.BooleanField('置顶', default=False)
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-is_top', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # 如果 slug 为空，或者标题被修改了，就重新生成 slug
        if not self.slug:
            # 1. 基于标题生成基础 slug
            base_slug = slugify(self.title)
            # 2. 检查这个基础 slug 是否已存在
            slug = base_slug
            num = 1
            # 3. 如果存在，就在后面加上数字，直到找到一个唯一的
            while Article.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num += 1
            # 4. 将最终唯一的 slug 赋值给 self.slug
            self.slug = slug
        
        # 调用父类的 save 方法，保存文章
        super().save(*args, **kwargs)

    
    def get_absolute_url(self):
        return reverse('articles:article_detail', kwargs={'slug': self.slug})
    
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])
    
    
