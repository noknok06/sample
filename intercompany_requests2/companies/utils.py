from django.conf import settings
from .models import Company

def get_or_create_default_company(name="デモ企業"):
    """
    デフォルト企業を取得または作成する
    開発環境でのテスト用
    """
    company, created = Company.objects.get_or_create(
        name=name,
        defaults={
            'industry': 'IT',
            'description': '開発用デモ企業',
            'is_active': True
        }
    )
    
    return company