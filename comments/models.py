from django.db import models
from django.contrib.auth import get_user_model
from articles.models import Article

User = get_user_model()

class Comment(models.Model):
    """评论模型"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name='文章')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='作者')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    content = models.TextField('评论内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_approved = models.BooleanField('审核通过', default=True)
    likes = models.PositiveIntegerField('点赞数', default=0)
    image = models.ImageField('评论图片', upload_to='comment_images/', null=True, blank=True) 
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.author.username} on {self.article.title}'
    
    def get_reply_count(self):
        """获取回复数量"""
        return self.replies.count()
