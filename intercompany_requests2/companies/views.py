from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse

from .models import Company, CompanyConnection
from .forms import CompanyForm, CompanyConnectionForm, CompanyInviteForm, CompanyJoinForm
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def company_list(request):
    """企業一覧表示"""
    # ユーザーの企業を取得
    user_company = request.user.company
    
    # ユーザーが企業に所属していない場合は企業参加ページへリダイレクト
    if not user_company:
        messages.warning(request, _('最初に企業に所属する必要があります。'))
        return redirect('companies:join')
    
    # 接続している企業を取得
    connected_companies = Company.objects.filter(
        incoming_connections__company_from=user_company,
        incoming_connections__status='accepted'
    ).order_by('name')
    
    context = {
        'user_company': user_company,
        'connected_companies': connected_companies,
        'title': _('企業一覧'),
    }
    
    return render(request, 'companies/company_list.html', context)

@login_required
def company_detail(request, pk):
    """企業詳細表示"""
    company = get_object_or_404(Company, pk=pk)
    
    # 自社か接続済みの企業のみ表示可能
    if request.user.company != company:
        connection = CompanyConnection.objects.filter(
            company_from=request.user.company,
            company_to=company,
            status='accepted'
        ).first()
        
        if not connection and not request.user.is_superuser:
            messages.error(request, _('You do not have permission to view this company.'))
            return redirect('companies:list')
    
    # 企業のユーザー一覧取得
    users = User.objects.filter(company=company)
    
    context = {
        'company': company,
        'users': users,
        'title': company.name,
    }
    
    return render(request, 'companies/company_detail.html', context)

@login_required
def company_edit(request, pk):
    """企業情報編集"""
    company = get_object_or_404(Company, pk=pk)
    
    # 自社のみ編集可能
    if request.user.company != company and not request.user.is_superuser:
        messages.error(request, _('You do not have permission to edit this company.'))
        return redirect('companies:detail', pk=pk)
    
    # 管理者権限がない場合は編集不可
    if not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, _('Only administrators can edit company information.'))
        return redirect('companies:detail', pk=pk)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, _('Company information updated successfully.'))
            return redirect('companies:detail', pk=pk)
    else:
        form = CompanyForm(instance=company)
    
    context = {
        'form': form,
        'company': company,
        'title': _('Edit Company'),
    }
    
    return render(request, 'companies/company_form.html', context)

@login_required
def company_create(request):
    """企業作成"""
    # 開発環境以外では管理者権限のみ許可
    if not settings.DEBUG and not request.user.is_admin and not request.user.is_superuser:
        messages.error(request, _('この操作を行う権限がありません。'))
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            
            # ユーザーが企業に未所属なら、作成した企業に所属させる
            if not request.user.company:
                request.user.company = company
                # 最初のユーザーは管理者にする
                request.user.role = 'admin'
                request.user.save()
            
            messages.success(request, _('企業が作成されました。'))
            return redirect('companies:detail', pk=company.pk)
    else:
        # 開発環境用の初期値
        initial_data = {}
        if settings.DEBUG:
            import random
            initial_data = {
                'name': f'テスト企業 {random.randint(1000, 9999)}',
                'industry': 'IT・テクノロジー',
                'email': f'test{random.randint(1000, 9999)}@example.com',
                'phone': f'03-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
            }
        
        form = CompanyForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': _('企業作成'),
        'is_development': settings.DEBUG,
    }
    
    return render(request, 'companies/company_form.html', context)

@login_required
def company_invite(request):
    """他ユーザーを企業に招待"""
    if not request.user.company:
        messages.error(request, _('You need to be associated with a company to invite users.'))
        return redirect('dashboard:home')
    
    # 管理者と管理者のみ招待可能
    if not request.user.is_admin and not request.user.is_manager:
        messages.error(request, _('Only administrators and managers can invite users.'))
        return redirect('companies:detail', pk=request.user.company.pk)
    
    if request.method == 'POST':
        form = CompanyInviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            company = request.user.company
            
            # 既存ユーザーをチェック
            existing_user = User.objects.filter(email=email).first()
            if existing_user and existing_user.company == company:
                messages.warning(request, _('This user is already a member of your company.'))
                return redirect('companies:invite')
            
            # 招待メール送信
            invite_url = request.build_absolute_uri(
                f"{reverse('companies:join')}?code={company.invitation_code}"
            )
            
            email_body = _("""
            You have been invited to join {company} on InterConnect.
            
            {message}
            
            To accept the invitation, please click the link below:
            {invite_url}
            
            Thank you,
            The InterConnect Team
            """).format(
                company=company.name,
                message=message if message else '',
                invite_url=invite_url
            )
            
            # 実際の環境では実際にメール送信する
            # send_mail(
            #     subject=_('Invitation to join {company} on InterConnect').format(company=company.name),
            #     message=email_body,
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[email],
            #     fail_silently=False,
            # )
            
            # 開発環境では送信せず成功メッセージを表示
            messages.success(
                request, 
                _('Invitation sent to {email}. Invitation URL: {url}').format(email=email, url=invite_url)
            )
            return redirect('companies:detail', pk=company.pk)
    else:
        form = CompanyInviteForm()
    
    context = {
        'form': form,
        'title': _('Invite User'),
    }
    
    return render(request, 'companies/company_invite.html', context)

@login_required
def company_join(request):
    """企業参加"""
    # すでに企業に所属している場合はリダイレクト
    if request.user.company:
        messages.info(request, _('あなたはすでに企業に所属しています。'))
        return redirect('dashboard:home')
    
    # 開発環境では自動企業作成オプションを表示
    is_development = settings.DEBUG
    
    if request.method == 'POST':
        # 開発モードでの自動参加処理
        if is_development and 'join_demo' in request.POST:
            from .utils import get_or_create_default_company
            company = get_or_create_default_company()
            request.user.company = company
            request.user.save()
            
            messages.success(request, _('デモ企業に参加しました。'))
            return redirect('dashboard:home')
        
        # 通常の招待コード処理
        form = CompanyJoinForm(request.POST)
        if form.is_valid():
            invitation_code = form.cleaned_data['invitation_code']
            
            try:
                company = Company.objects.get(invitation_code=invitation_code)
                request.user.company = company
                request.user.save()
                
                messages.success(request, _('企業に参加しました。'))
                return redirect('dashboard:home')
            except Company.DoesNotExist:
                form.add_error('invitation_code', _('無効な招待コードです。'))
    else:
        form = CompanyJoinForm()
    
    context = {
        'form': form,
        'title': _('企業参加'),
        'is_development': is_development,
    }
    
    return render(request, 'companies/company_join.html', context)

@login_required
def company_connect(request):
    """他企業との連携を申請"""
    if not request.user.company:
        messages.error(request, _('You need to be associated with a company to connect with others.'))
        return redirect('dashboard:home')
    
    # 管理者と管理者のみ連携申請可能
    if not request.user.is_admin and not request.user.is_manager:
        messages.error(request, _('Only administrators and managers can connect with other companies.'))
        return redirect('companies:list')
    
    if request.method == 'POST':
        form = CompanyConnectionForm(request.POST, current_company=request.user.company)
        if form.is_valid():
            # デバッグ: フォームと現在の企業の情報を出力
            print("\n--- 接続リクエスト作成 ---")
            print(f"現在の企業: {request.user.company}")
            print(f"選択された企業: {form.cleaned_data['company_to']}")
            
            # 連携申請の作成
            connection = CompanyConnection(
                company_from=request.user.company,
                company_to=form.cleaned_data['company_to'],
                status='pending'
            )
            connection.save()
            
            # デバッグ: 保存された接続リクエストの情報を出力
            print(f"保存された接続リクエスト:")
            print(f"ID: {connection.id}")
            print(f"From: {connection.company_from}")
            print(f"To: {connection.company_to}")
            print(f"Status: {connection.status}")
            print("---")
            
            messages.success(
                request, 
                _('Connection request sent to {company}.').format(
                    company=form.cleaned_data['company_to'].name
                )
            )
            return redirect('companies:connections')
    else:
        form = CompanyConnectionForm(current_company=request.user.company)
    
    context = {
        'form': form,
        'title': _('Connect with Company'),
    }
    
    return render(request, 'companies/company_connect.html', context)

@login_required
def connection_list(request):
    """企業連携一覧表示"""
    # デバッグ: ログインユーザーと企業の情報
    print("\n--- デバッグ情報 ---")
    print(f"ログインユーザー: {request.user}")
    print(f"ユーザーの企業: {request.user.company}")
    
    if not request.user.company:
        messages.error(request, _('You need to be associated with a company to view connections.'))
        return redirect('dashboard:home')
    
    # すべての接続リクエストを詳細に出力
    all_connections = CompanyConnection.objects.all()
    print("\n--- すべての接続リクエスト ---")
    for conn in all_connections:
        print(f"ID: {conn.id}")
        print(f"From: {conn.company_from}")
        print(f"To: {conn.company_to}")
        print(f"Status: {conn.status}")
        print("---")
    
    # 現在のユーザーの企業に関連する接続リクエストのみを取得
    user_company = request.user.company
    
    # 送信した連携申請: 現在のユーザーの企業が送信元
    outgoing = CompanyConnection.objects.filter(
        company_from=user_company
    ).select_related('company_to')
    
    # 受信した連携申請: 現在のユーザーの企業が送信先
    incoming = CompanyConnection.objects.filter(
        company_to=user_company
    ).select_related('company_from')
    
    # 詳細デバッグ情報の出力
    print("\n--- 送信した接続リクエスト ---")
    for conn in outgoing:
        print(f"ID: {conn.id}")
        print(f"To: {conn.company_to}")
        print(f"Status: {conn.status}")
        print("---")
    
    print("\n--- 受信した接続リクエスト ---")
    for conn in incoming:
        print(f"ID: {conn.id}")
        print(f"From: {conn.company_from}")
        print(f"Status: {conn.status}")
        print("---")
    
    # 追加のデバッグ情報
    print(f"\n送信リクエスト数: {outgoing.count()}")
    print(f"受信リクエスト数: {incoming.count()}")
    
    context = {
        'outgoing': outgoing,
        'incoming': incoming,
        'title': _('Company Connections'),
    }
    
    return render(request, 'companies/connection_list.html', context)

@login_required
def connection_respond(request, pk):
    """連携申請への応答（承認/拒否）"""
    connection = get_object_or_404(
        CompanyConnection, 
        pk=pk, 
        company_to=request.user.company,
        status='pending'
    )
    
    # 管理者と管理者のみ連携申請に回答可能
    if not request.user.is_admin and not request.user.is_manager:
        messages.error(request, _('Only administrators and managers can respond to connection requests.'))
        return redirect('companies:connections')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accept':
            connection.status = 'accepted'
            connection.save()
            
            # 相互接続を自動的に作成
            reverse_connection, created = CompanyConnection.objects.get_or_create(
                company_from=connection.company_to,
                company_to=connection.company_from,
                defaults={'status': 'accepted'}
            )
            
            if not created:
                reverse_connection.status = 'accepted'
                reverse_connection.save()
            
            messages.success(
                request, 
                _('Connection with {company} has been accepted.').format(
                    company=connection.company_from.name
                )
            )
        elif action == 'reject':
            connection.status = 'rejected'
            connection.save()
            messages.success(
                request, 
                _('Connection with {company} has been rejected.').format(
                    company=connection.company_from.name
                )
            )
        
        return redirect('companies:connections')
    
    context = {
        'connection': connection,
        'title': _('Respond to Connection Request'),
    }
    
    return render(request, 'companies/connection_respond.html', context)