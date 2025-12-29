from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.conf import settings
import logging
from .models import Comment
from django.contrib.contenttypes.models import ContentType
from core.models import Notification

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        # 如果是回复评论 -> 通知父评论作者
        if instance.parent:
            parent_comment = instance.parent
            author = parent_comment.author
            try:
                Notification.objects.create(
                    recipient=author,
                    actor=instance.author,
                    verb='回复了你的评论',
                    target_content_type=ContentType.objects.get_for_model(Comment),
                    target_object_id=instance.id,
                    data={
                        'article_id': instance.article.id,
                        'article_slug': getattr(instance.article, 'slug', None),
                        'comment_id': instance.id,
                        'comment_excerpt': instance.content[:120]
                    }
                )
            except Exception as e:
                logger.exception('创建回复通知失败: %s', e)
        else:
            # 顶级评论 -> 通知文章作者
            article_author = instance.article.author
            try:
                if article_author:
                    Notification.objects.create(
                        recipient=article_author,
                        actor=instance.author,
                        verb='在你的文章发表评论',
                        target_content_type=ContentType.objects.get_for_model(Comment),
                        target_object_id=instance.id,
                        data={
                            'article_id': instance.article.id,
                            'article_slug': getattr(instance.article, 'slug', None),
                            'comment_id': instance.id,
                            'comment_excerpt': instance.content[:120]
                        }
                    )
            except Exception as e:
                logger.exception('创建文章评论通知失败: %s', e)
  