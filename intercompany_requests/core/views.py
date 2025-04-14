# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count, Q
from .models import Company, Request, Comment, Attachment, Activity, User
from .forms import RequestForm, CommentForm, CompanyForm

@login_required
def dashboard(request):
    """ダッシュボード表示"""
    user = request.user
    company = user.company
    
    # 自社関連の要望を取得
    pending_requests = Request.objects.filter(
        Q(sender_company=company) | Q(receiver_company=company),
        status='pending'
    ).order_by('-created_at')[:5]
    
    approved_requests = Request.objects.filter(
        Q(sender_company=company) | Q(receiver_company=company),
        status='approved'
    ).order_by('-created_at')[:5]
    
    completed_requests = Request.objects.filter(
        Q(sender_company=company) | Q(receiver_company=company),
        status='completed'
    ).order_by('-created_at')[:5]
    
    # 最近のアクティビティを取得
    recent_activities = Activity.objects.filter(
        request__in=Request.objects.filter(
            Q(sender_company=company) | Q(receiver_company=company)
        )
    ).order_by('-created_at')[:5]
    
    # 接続企業を取得
    connected_companies = Company.objects.filter(
        Q(sent_requests__receiver_company=company) | 
        Q(received_requests__sender_company=company)
    ).distinct()
    
    # 統計データ
    total_requests = Request.objects.filter(
        Q(sender_company=company) | Q(receiver_company=company)
    ).count()
    
    pending_count = Request.objects.filter(
        Q(sender_company=company) | Q(receiver_company=company),
        status='pending'
    ).count()
    
    approved_count = Request.objects.filter(
        Q(sender_company=company) | Q(receiver_company=company),
        status='approved'
    ).count()
    
    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'completed_requests': completed_requests,
        'recent_activities': recent_activities,
        'connected_companies': connected_companies,
        'total_requests': total_requests,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'connected_count': connected_companies.count(),
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def company_list(request):
    """会社一覧表示"""
    user = request.user
    company = user.company
    
    # 接続されている企業を取得
    connected_companies = Company.objects.filter(
        Q(sent_requests__receiver_company=company) | 
        Q(received_requests__sender_company=company)
    ).distinct().annotate(
        contact_count=Count('employees', distinct=True),
        active_request_count=Count('received_requests', 
                                  filter=~Q(received_requests__status__in=['completed', 'rejected']),
                                  distinct=True)
    )
    
    # 検索フィルタ処理
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    if status_filter != 'all':
        connected_companies = connected_companies.filter(status=status_filter)
    
    if search_query:
        connected_companies = connected_companies.filter(
            Q(name__icontains=search_query) | 
            Q(industry__icontains=search_query)
        )
    
    context = {
        'companies': connected_companies,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'companies/list.html', context)

@login_required
def request_detail(request, pk):
    """要望の詳細表示"""
    req = get_object_or_404(Request, pk=pk)
    user = request.user
    company = user.company
    
    # 関連企業の要望のみアクセス可能にする
    if req.sender_company != company and req.receiver_company != company:
        messages.error(request, "この要望にアクセスする権限がありません。")
        return redirect('dashboard')
    
    # コメント投稿処理
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.request = req
            comment.user = user
            comment.save()
            
            # アクティビティ記録
            Activity.objects.create(
                request=req,
                user=user,
                action=f"{user.username}がコメントを追加しました"
            )
            
            messages.success(request, "コメントが追加されました。")
            return redirect('request_detail', pk=pk)
    else:
        form = CommentForm()
    
    # 要望のステータス更新処理（HTMX対応）
    if request.headers.get('HX-Request') and 'status' in request.GET:
        new_status = request.GET.get('status')
        if new_status in dict(Request.STATUS_CHOICES).keys():
            req.status = new_status
            req.save()
            
            # アクティビティ記録
            Activity.objects.create(
                request=req,
                user=user,
                action=f"{user.username}が要望のステータスを「{dict(Request.STATUS_CHOICES)[new_status]}」に変更しました"
            )
            
            # HTMX部分更新用レスポンス
            return render(request, 'requests/partials/status_badge.html', {'request': req})
    
    context = {
        'request': req,
        'comments': req.comments.all().order_by('created_at'),
        'activities': req.activities.all().order_by('-created_at'),
        'form': form,
    }
    
    return render(request, 'requests/detail.html', context)

@login_required
def new_request(request):
    """新規要望作成"""
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.sender_company = request.user.company
            req.requester = request.user
            req.save()
            
            # 添付ファイル処理
            for file in request.FILES.getlist('attachments'):
                Attachment.objects.create(
                    request=req,
                    file=file,
                    name=file.name,
                    size=file.size,
                    uploaded_by=request.user
                )
            
            # アクティビティ記録
            Activity.objects.create(
                request=req,
                user=request.user,
                action=f"{request.user.username}が新しい要望を作成しました"
            )
            
            messages.success(request, "要望が正常に作成されました。")
            return redirect('request_detail', pk=req.pk)
    else:
        # 自社以外の接続企業のみをフォームの選択肢に含める
        user_company = request.user.company
        connected_companies = Company.objects.filter(
            Q(sent_requests__receiver_company=user_company) | 
            Q(received_requests__sender_company=user_company)
        ).distinct().exclude(id=user_company.id)
        
        form = RequestForm()
        form.fields['receiver_company'].queryset = connected_companies
    
    context = {
        'form': form,
    }
    
    return render(request, 'requests/new.html', context)