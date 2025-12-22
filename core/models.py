# core/models.py
from django.db import models

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
