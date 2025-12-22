from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Comment

@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
      if created and instance.parent:  # 如果是回复评论
          parent_comment = instance.parent
          author = parent_comment.author
          if author != instance.author:  # 不给自己发通知
              subject = '有人回复了你的评论'
              html_message = render_to_string('notifications/comment_reply.html', {
                  'comment': instance,
                  'article': instance.article,
              })
              send_mail(subject, '', 'noreply@example.com', [author.email], html_message=html_message)
  