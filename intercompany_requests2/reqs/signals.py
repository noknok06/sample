from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Request, RequestApproval, Attachment
from notifications.services import NotificationService

@receiver(post_save, sender=Request)
def request_saved(sender, instance, created, **kwargs):
    """リクエストが作成または更新された時のシグナルハンドラ"""
    if created:
        # 新しいリクエストが作成された場合
        NotificationService.create_request_notification(instance, 'request_created')
        
        # 承認者がいる場合、最初の承認者に通知
        if instance.get_next_approver():
            NotificationService.create_request_notification(instance, 'approval_needed')
    else:
        # リクエストが更新された場合
        # ステータスが変わった場合にのみ通知を送信
        if 'status' in kwargs.get('update_fields', []):
            if instance.status == 'approved':
                NotificationService.create_request_notification(instance, 'request_approved')
            elif instance.status == 'rejected':
                NotificationService.create_request_notification(instance, 'request_rejected')
            else:
                NotificationService.create_request_notification(instance, 'request_updated')

@receiver(post_save, sender=RequestApproval)
def approval_saved(sender, instance, created, **kwargs):
    """承認が更新された時のシグナルハンドラ"""
    if not created:
        # 承認ステータスが更新された場合
        request = instance.request
        
        # 承認ステータスに基づいて処理
        if instance.status == 'approved':
            # 次の承認者がいれば通知
            next_approver = request.get_next_approver()
            if next_approver:
                # このリクエストに承認が必要なことを次の承認者に通知
                NotificationService.create_notification(
                    next_approver, 
                    request, 
                    'approval_needed'
                )
            else:
                # すべての承認が完了した場合、リクエストを承認済みにする
                if request.status != 'approved':
                    request.status = 'approved'
                    request.save(update_fields=['status'])
                
                # リクエスト作成者に承認完了を通知
                NotificationService.create_notification(
                    request.creator,
                    request,
                    'request_approved'
                )
        
        elif instance.status == 'rejected':
            # リクエストを却下状態に更新
            if request.status != 'rejected':
                request.status = 'rejected'
                request.save(update_fields=['status'])
            
            # リクエスト作成者に却下を通知
            NotificationService.create_notification(
                request.creator,
                request,
                'request_rejected'
            )