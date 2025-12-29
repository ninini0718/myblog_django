# core/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class NotificationManager(models.Manager):
    def unread(self):
        return self.filter(unread=True)

    @property
    def unread_count(self):
        return self.filter(unread=True).count()


class Notification(models.Model):
    """通用通知模型，用于保存站内通知（e.g. 评论回复、文章新评论等）"""
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='接收者')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications_from', verbose_name='触发者')
    verb = models.CharField('动作描述', max_length=255)

    # 可指向任意对象（例如 Comment、Article）
    target_content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    target_object_id = models.CharField(max_length=255, null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    unread = models.BooleanField('未读', default=True)
    timestamp = models.DateTimeField('时间', auto_now_add=True)
    data = models.JSONField('额外数据', null=True, blank=True)

    objects = NotificationManager()

    class Meta:
        ordering = ['-timestamp']
        verbose_name = '通知'
        verbose_name_plural = '通知'

    def __str__(self):
        return f"通知 to {self.recipient} - {self.verb}"

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save(update_fields=['unread'])

    @classmethod
    def mark_all_read(cls, user):
        cls.objects.filter(recipient=user, unread=True).update(unread=False)

class BlogSettings(models.Model):
    """
    博客全局设置模型，用于存储主题、标题等全局信息。
    """
    site_title = models.CharField('网站标题', max_length=200, default='Django博客')
    site_description = models.TextField('网站描述', blank=True)
    background_image = models.ImageField('背景图片', upload_to='backgrounds/', blank=True, null=True)
    
    # 主题选择，提供几个预设选项
    THEME_CHOICES = [
        ('default', '默认主题'),
        ('dark', '暗黑主题'),
        ('light', '明亮主题'),
    ]
    active_theme = models.CharField(
        '当前主题', 
        max_length=20, 
        choices=THEME_CHOICES, 
        default='default'
    )

    class Meta:
        verbose_name = '博客设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        # 确保数据库中始终只有一条设置记录
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        一个便捷方法，用于加载唯一的设置实例。
        如果不存在，则创建一个默认的。
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
