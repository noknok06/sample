from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Comment
from notifications.services import NotificationService

@receiver(post_save, sender=Comment)
def comment_saved(sender, instance, created, **kwargs):
    """コメントが作成された時のシグナルハンドラ"""
    if created:
        # 新しいコメントが作成された場合
        NotificationService.create_comment_notification(instance)