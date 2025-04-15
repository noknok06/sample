from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Company, CompanyConnection

@receiver(post_save, sender=Company)
def company_saved(sender, instance, created, **kwargs):
    """Signal handler for when a company is created or updated."""
    # ここに会社作成・更新時の処理を追加
    pass

@receiver(post_save, sender=CompanyConnection)
def company_connection_saved(sender, instance, created, **kwargs):
    """Signal handler for when a company connection is created or updated."""
    # ここに会社間接続時の処理を追加
    pass