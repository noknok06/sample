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
    user = request.user
    
    # ユーザーに会社が割り当てられていない場合のハンドリング
    if not user.company:
        messages.error(request, "要望を作成するには、まず会社情報を設定してください。")
        return redirect('profile')  # プロフィール設定ページへリダイレクト
    
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.sender_company = user.company
            req.requester = user
            req.save()
            
            # 添付ファイル処理
            for file in request.FILES.getlist('attachments'):
                Attachment.objects.create(
                    request=req,
                    file=file,
                    name=file.name,
                    size=file.size,
                    uploaded_by=user
                )
            
            # アクティビティ記録
            Activity.objects.create(
                request=req,
                user=user,
                action=f"{user.username}が新しい要望を作成しました"
            )
            
            messages.success(request, "要望が正常に作成されました。")
            return redirect('request_detail', pk=req.pk)
    else:
        # デバッグ用のコンソール出力
        print("User's company:", user.company)
        
        # 接続企業を取得（自社以外）
        connected_companies = Company.objects.filter(
            Q(sent_requests__receiver_company=user.company) | 
            Q(received_requests__sender_company=user.company)
        ).distinct().exclude(id=user.company.id)
        
        # デバッグ用のコンソール出力
        print("Connected companies:", list(connected_companies.values('id', 'name')))
        
        # フォームを初期化し、接続企業を選択肢に設定
        form = RequestForm()
        
        # クエリセットを設定 (form.fields['receiver_company']が存在することを確認)
        if hasattr(form.fields, 'receiver_company'):
            form.fields['receiver_company'].queryset = connected_companies
        else:
            # フィールドが存在しない場合のデバッグ情報
            print("Form fields:", list(form.fields.keys()))
    
    context = {
        'form': form,
    }
    
    return render(request, 'requests/new.html', context)

# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings

from .models import Company, Request, Comment, Attachment, Activity, User
from .forms import RequestForm, CommentForm, CompanyForm, UserProfileForm

# 既存のビュー関数をそのまま保持

@login_required
def request_list(request):
    """リクエスト一覧の表示"""
    user = request.user
    company = user.company
    
    # リクエストの基本クエリセット
    requests_qs = Request.objects.filter(
        Q(sender_company=company) | Q(receiver_company=company)
    ).order_by('-created_at')
    
    # 検索とフィルタリング
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    priority_filter = request.GET.get('priority', 'all')
    company_filter = request.GET.get('company', 'all')
    
    # 検索条件の適用
    if search_query:
        requests_qs = requests_qs.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # ステータスフィルタ
    if status_filter != 'all':
        requests_qs = requests_qs.filter(status=status_filter)
    
    # 優先度フィルタ
    if priority_filter != 'all':
        requests_qs = requests_qs.filter(priority=priority_filter)
    
    # 企業フィルタ
    if company_filter != 'all':
        requests_qs = requests_qs.filter(
            Q(sender_company_id=company_filter) | 
            Q(receiver_company_id=company_filter)
        )
    
    # ページネーション
    paginator = Paginator(requests_qs, 10)  # 1ページあたり10件
    page = request.GET.get('page', 1)
    
    try:
        requests = paginator.page(page)
    except PageNotAnInteger:
        requests = paginator.page(1)
    except EmptyPage:
        requests = paginator.page(paginator.num_pages)
    
    # 接続企業一覧（フィルタ用）
    connected_companies = Company.objects.filter(
        Q(sent_requests__receiver_company=company) | 
        Q(received_requests__sender_company=company)
    ).distinct()
    
    context = {
        'requests': requests,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'company_filter': company_filter,
        'companies': connected_companies,
        'now': timezone.now(),
    }
    
    return render(request, 'requests/list.html', context)

@login_required
def company_detail(request, pk):
    """会社の詳細表示"""
    company = get_object_or_404(Company, pk=pk)
    user = request.user
    
    # アクセス制限: 接続されている企業のみ閲覧可能
    connected_companies = Company.objects.filter(
        Q(sent_requests__receiver_company=user.company) | 
        Q(received_requests__sender_company=user.company)
    ).distinct()
    
    if company not in connected_companies and company != user.company:
        messages.error(request, "この企業の詳細を閲覧する権限がありません。")
        return redirect('dashboard')
    
    # 企業の担当者取得
    contacts = User.objects.filter(company=company)
    
    # リクエスト履歴
    requests = Request.objects.filter(
        Q(sender_company=company) | Q(receiver_company=company)
    ).order_by('-created_at')
    
    # ページネーション
    paginator = Paginator(requests, 5)  # 1ページあたり5件
    page = request.GET.get('page', 1)
    
    try:
        requests = paginator.page(page)
    except PageNotAnInteger:
        requests = paginator.page(1)
    except EmptyPage:
        requests = paginator.page(paginator.num_pages)
    
    context = {
        'company': company,
        'contacts': contacts,
        'requests': requests,
    }
    
    return render(request, 'companies/detail.html', context)

@login_required
def company_new(request):
    """新規会社登録"""
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(request, f"{company.name}が正常に登録されました。")
            return redirect('company_detail', pk=company.pk)
    else:
        form = CompanyForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'companies/new.html', context)

@login_required
def company_edit(request, pk):
    """会社情報編集"""
    company = get_object_or_404(Company, pk=pk)
    
    # アクセス制限
    if request.user.company != company and not request.user.is_superuser:
        messages.error(request, "この企業を編集する権限がありません。")
        return redirect('company_detail', pk=pk)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f"{company.name}の情報が更新されました。")
            return redirect('company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    
    context = {
        'company': company,
        'form': form,
    }
    
    return render(request, 'companies/edit.html', context)

@login_required
def company_invite(request):
    """企業招待"""
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message', '')
        
        # メール送信のロジック（実際の運用では招待システムをより詳細に実装）
        try:
            send_mail(
                f'{request.user.company.name}からの企業招待',
                f"""
{request.user.get_full_name()}が、InterConnectプラットフォームに招待しています。

メッセージ:
{message}

招待を受け入れるには、以下のリンクをクリックしてください。
{settings.BASE_URL}/invite
""",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, f"{email}に招待メールを送信しました。")
        except Exception as e:
            messages.error(request, "招待メールの送信に失敗しました。")
        
        return redirect('company_list')
    
    return redirect('company_list')

@login_required
def profile(request):
    """ユーザープロフィール表示・編集"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "プロフィールが更新されました。")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def settings(request):
    """ユーザー設定"""
    # 将来的な設定ページの実装
    context = {
        'user': request.user,
    }
    
    return render(request, 'users/settings.html', context)

# 認証関連のビュー
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

def login_view(request):
    """ログインビュー"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"ようこそ、{user.username}さん！")
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'auth/login.html', context)

def logout_view(request):
    """ログアウトビュー"""
    logout(request)
    messages.success(request, "ログアウトしました。")
    return redirect('login')

def register(request):
    """ユーザー登録ビュー"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        company_name = request.POST.get('company_name')
        role = request.POST.get('role', '')
        
        if form.is_valid():
            # 企業の作成
            company, created = Company.objects.get_or_create(
                name=company_name,
                defaults={
                    'industry': 'その他',
                    'email': form.cleaned_data.get('email'),
                    'status': 'active'
                }
            )
            
            # ユーザーの作成
            user = form.save(commit=False)
            user.company = company
            user.role = role
            user.save()
            
            # 自動ログイン
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"ようこそ、{user.username}さん！")
                return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'auth/register.html', context)

# その他の静的ページ
def features(request):
    """機能紹介ページ"""
    return render(request, 'pages/features.html')

def pricing(request):
    """料金ページ"""
    return render(request, 'pages/pricing.html')

def about(request):
    """会社概要ページ"""
    return render(request, 'pages/about.html')

def contact(request):
    """お問い合わせページ"""
    if request.method == 'POST':
        # お問い合わせフォーム処理のロジック
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        try:
            send_mail(
                f'お問い合わせ: {name}',
                f"""
名前: {name}
メール: {email}

メッセージ:
{message}
""",
                email,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "お問い合わせを受け付けました。")
        except Exception as e:
            messages.error(request, "メッセージの送信に失敗しました。")
        
        return redirect('contact')
    
    return render(request, 'pages/contact.html')

# コメント関連ビュー
@login_required
def add_comment(request, request_id):
    """コメント追加"""
    req = get_object_or_404(Request, pk=request_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.request = req
            comment.user = request.user
            comment.save()
            
            # アクティビティ記録
            Activity.objects.create(
                request=req,
                user=request.user,
                action=f"{request.user.username}がコメントを追加しました"
            )
            
            # HTMX対応のレスポンス
            return render(request, 'requests/partials/comment.html', {'comment': comment})
    
    return HttpResponse("コメントの追加に失敗しました", status=400)

@login_required
def like_comment(request, pk):
    """コメントへのいいね（未実装）"""
    comment = get_object_or_404(Comment, pk=pk)
    
    # いいね機能の実装（将来の拡張）
    return render(request, 'requests/partials/like_button.html', {'comment': comment})

@login_required
def reply_form(request, pk, request_id):
    """コメント返信フォーム"""
    comment = get_object_or_404(Comment, pk=pk)
    req = get_object_or_404(Request, pk=request_id)
    
    context = {
        'comment': comment,
        'request': req,
    }
    
    return render(request, 'requests/partials/reply_form.html', context)

@login_required
def comment_form(request, request_id):
    """コメントフォーム"""
    req = get_object_or_404(Request, pk=request_id)
    form = CommentForm()
    
    context = {
        'request': req,
        'form': form,
    }
    
    return render(request, 'requests/partials/comment_form.html', context)

# 必要なインポート
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm

@login_required
def update_request_status(request, pk):
    """要望のステータス更新"""
    req = get_object_or_404(Request, pk=pk)
    new_status = request.GET.get('status')
    
    # アクセス制限: 受信企業の担当者のみステータス変更可能
    if req.receiver_company != request.user.company:
        return HttpResponseForbidden("このリクエストのステータスを変更する権限がありません。")
    
    if new_status in dict(Request.STATUS_CHOICES).keys():
        req.status = new_status
        req.save()
        
        # アクティビティ記録
        Activity.objects.create(
            request=req,
            user=request.user,
            action=f"{request.user.username}が要望のステータスを「{dict(Request.STATUS_CHOICES)[new_status]}」に変更しました"
        )
        
        # HTMX対応のレスポンス
        return render(request, 'requests/partials/status_badge.html', {'request': req})
    
    return HttpResponse("無効なステータスです", status=400)

@login_required
def request_status(request, pk):
    """リクエストステータスバッジ表示用"""
    req = get_object_or_404(Request, pk=pk)
    return render(request, 'requests/partials/status_badge.html', {'request': req})

# 活動履歴リスト
@login_required
def activity_list(request):
    """活動履歴一覧表示"""
    user = request.user
    company = user.company
    
    # 自社に関連する活動履歴
    activities = Activity.objects.filter(
        request__in=Request.objects.filter(
            Q(sender_company=company) | Q(receiver_company=company)
        )
    ).order_by('-created_at')
    
    # ページネーション
    paginator = Paginator(activities, 20)  # 1ページあたり20件
    page = request.GET.get('page', 1)
    
    try:
        activities = paginator.page(page)
    except PageNotAnInteger:
        activities = paginator.page(1)
    except EmptyPage:
        activities = paginator.page(paginator.num_pages)
    
    context = {
        'activities': activities,
    }
    
    return render(request, 'activities/list.html', context)

from .forms import CustomUserCreationForm

def register(request):
    """ユーザー登録ビュー"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # フォームのsave()メソッドで会社とユーザーの作成が行われます
            user = form.save()
            
            # 自動ログイン
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"ようこそ、{user.username}さん！")
                return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'auth/register.html', context)
