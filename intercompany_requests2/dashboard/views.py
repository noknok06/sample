from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from reqs.models import Request, RequestApproval
from comments.models import Comment

@login_required
def home(request):
    """ダッシュボードホーム"""
    # ユーザーの企業が設定されていない場合は企業参加ページへリダイレクト
    if not request.user.company:
        return redirect('companies:join')
    
    user = request.user
    company = user.company
    
    # 基本的なリクエスト統計
    requests_stats = {
        'total': Request.objects.filter(
            Q(company_from=company) | Q(company_to=company)
        ).count(),
        'pending': Request.objects.filter(
            (Q(company_from=company) | Q(company_to=company)) &
            Q(status='pending')
        ).count(),
        'approved': Request.objects.filter(
            (Q(company_from=company) | Q(company_to=company)) &
            Q(status='approved')
        ).count(),
        'rejected': Request.objects.filter(
            (Q(company_from=company) | Q(company_to=company)) &
            Q(status='rejected')
        ).count(),
        'needs_approval': RequestApproval.objects.filter(
            approver=user,
            status='pending'
        ).count(),
    }
    
    # 高優先度リクエスト
    priority_requests = Request.objects.filter(
        (Q(company_from=company) | Q(company_to=company)) &
        (Q(priority='high') | Q(priority='urgent')) &
        ~Q(status__in=['completed', 'cancelled', 'rejected'])
    ).order_by('-priority', 'deadline')[:5]
    
    # 期限間近のリクエスト（2週間以内）
    # 期限なしや期限切れは除外
    now = timezone.now().date()
    deadline_soon = Request.objects.filter(
        (Q(company_from=company) | Q(company_to=company)) &
        Q(deadline__isnull=False) &
        Q(deadline__gte=now) &
        Q(deadline__lte=now + timedelta(days=14)) &
        ~Q(status__in=['completed', 'cancelled', 'rejected'])
    ).order_by('deadline')[:5]
    
    # 最近の活動
    recent_requests = Request.objects.filter(
        (Q(company_from=company) | Q(company_to=company))
    ).order_by('-updated_at')[:5]
    
    recent_comments = Comment.objects.filter(
        (Q(request__company_from=company) | Q(request__company_to=company))
    ).select_related('author', 'request').order_by('-created_at')[:5]
    
    # 承認待ちリクエスト
    approval_requests = Request.objects.filter(
        approvals__approver=user,
        approvals__status='pending'
    ).order_by('-created_at')
    
    # 割り当てられたリクエスト
    assigned_requests = Request.objects.filter(
        assigned_to=user,
        # ~Q(status__in=['completed', 'cancelled', 'rejected'])
    ).order_by('-updated_at')
    
    # 作成したリクエスト
    created_requests = Request.objects.filter(
        creator=user,
        # ~Q(status__in=['completed', 'cancelled', 'rejected'])
    ).order_by('-updated_at')
    
    context = {
        'title': 'Dashboard',
        'requests_stats': requests_stats,
        'priority_requests': priority_requests,
        'deadline_soon': deadline_soon,
        'recent_requests': recent_requests,
        'recent_comments': recent_comments,
        'approval_requests': approval_requests,
        'assigned_requests': assigned_requests,
        'created_requests': created_requests,
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def activities(request):
    """アクティビティ履歴表示"""
    user = request.user
    company = user.company
    
    if not company:
        return redirect('companies:join')
    
    # リクエスト関連の活動
    recent_requests = Request.objects.filter(
        (Q(company_from=company) | Q(company_to=company))
    ).order_by('-updated_at')[:20]
    
    # コメント関連の活動
    recent_comments = Comment.objects.filter(
        (Q(request__company_from=company) | Q(request__company_to=company))
    ).select_related('author', 'request').order_by('-created_at')[:20]
    
    # 承認関連の活動
    recent_approvals = RequestApproval.objects.filter(
        (Q(request__company_from=company) | Q(request__company_to=company)) &
        ~Q(status='pending')
    ).select_related('approver', 'request').order_by('-updated_at')[:20]
    
    context = {
        'title': 'Activities',
        'recent_requests': recent_requests,
        'recent_comments': recent_comments,
        'recent_approvals': recent_approvals,
    }
    
    return render(request, 'dashboard/activities.html', context)

@login_required
def statistics(request):
    """統計情報表示"""
    user = request.user
    company = user.company
    
    if not company:
        return redirect('companies:join')
    
    # 期間別の統計（月別）
    this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 月別リクエスト統計
    monthly_stats = []
    for i in range(6):  # 過去6ヶ月
        month_start = this_month_start - timedelta(days=30*i)
        month_end = this_month_start - timedelta(days=30*(i-1)) if i > 0 else timezone.now()
        
        # この月に作成されたリクエスト
        created_count = Request.objects.filter(
            (Q(company_from=company) | Q(company_to=company)) &
            Q(created_at__gte=month_start) &
            Q(created_at__lt=month_end)
        ).count()
        
        # この月に完了したリクエスト
        completed_count = Request.objects.filter(
            (Q(company_from=company) | Q(company_to=company)) &
            Q(status='completed') &
            Q(updated_at__gte=month_start) &
            Q(updated_at__lt=month_end)
        ).count()
        
        # この月に却下されたリクエスト
        rejected_count = Request.objects.filter(
            (Q(company_from=company) | Q(company_to=company)) &
            Q(status='rejected') &
            Q(updated_at__gte=month_start) &
            Q(updated_at__lt=month_end)
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%Y年%m月'),
            'created': created_count,
            'completed': completed_count,
            'rejected': rejected_count,
        })
    
    # 企業内ユーザーごとの統計
    user_stats = []
    company_users = company.users.all()
    for user in company_users:
        user_stat = {
            'user': user,
            'created': Request.objects.filter(creator=user).count(),
            'assigned': Request.objects.filter(assigned_to=user).count(),
            'approved': RequestApproval.objects.filter(approver=user, status='approved').count(),
            'rejected': RequestApproval.objects.filter(approver=user, status='rejected').count(),
        }
        user_stats.append(user_stat)
    
    # カテゴリ別統計
    category_stats = Request.objects.filter(
        Q(company_from=company) | Q(company_to=company)
    ).values('category').annotate(count=Count('id')).order_by('-count')
    
    # ステータス別統計
    status_stats = Request.objects.filter(
        Q(company_from=company) | Q(company_to=company)
    ).values('status').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'title': 'Statistics',
        'monthly_stats': monthly_stats,
        'user_stats': user_stats,
        'category_stats': category_stats,
        'status_stats': status_stats,
    }
    
    return render(request, 'dashboard/statistics.html', context)