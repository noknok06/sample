from django.conf import settings

def site_settings(request):
    """
    コンテキストプロセッサ：サイト設定をすべてのテンプレートに追加
    """
    # 未読通知のカウント
    unread_count = 0
    if request.user.is_authenticated:
        try:
            unread_count = request.user.notifications.filter(is_read=False).count()
        except:
            # 通知モデルがまだ存在しない場合などのエラー対策
            unread_count = 0
    
    return {
        'SITE_NAME': 'InterConnect',
        'SITE_VERSION': '1.0.0',
        'DEBUG': settings.DEBUG,
        'unread_notifications_count': unread_count,  # 未読通知数を追加
    }