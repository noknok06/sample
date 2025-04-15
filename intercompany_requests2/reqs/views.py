from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q

from .models import Request, RequestApproval, Attachment
from .forms import RequestForm, RequestApprovalForm, RequestAttachmentForm, ApproverFormSet


@login_required
def request_list(request):
    """リクエスト一覧表示"""
    # フィルターパラメータの取得
    status = request.GET.get('status')
    priority = request.GET.get('priority')
    category = request.GET.get('category')
    direction = request.GET.get('direction', 'all')  # 'incoming', 'outgoing', 'all'
    search_query = request.GET.get('q', '')  # 検索クエリ
    date_from = request.GET.get('date_from')  # 日付範囲（開始）
    date_to = request.GET.get('date_to')  # 日付範囲（終了）
    
    # ベースクエリ - ユーザーの会社に関連するリクエスト
    user = request.user
    company = user.company
    
    if not company:
        messages.error(request, _('You need to be associated with a company to view requests.'))
        return redirect('dashboard:home')
    
    # 初期クエリセット
    if direction == 'incoming':
        requests = Request.objects.filter(company_to=company)
    elif direction == 'outgoing':
        requests = Request.objects.filter(company_from=company)
    else:  # 'all'
        requests = Request.objects.filter(Q(company_to=company) | Q(company_from=company))
    
    # フィルターの適用
    if status:
        requests = requests.filter(status=status)
    
    if priority:
        requests = requests.filter(priority=priority)
    
    if category:
        requests = requests.filter(category=category)
    
    # 検索クエリの適用
    if search_query:
        requests = requests.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(creator__first_name__icontains=search_query) |
            Q(creator__last_name__icontains=search_query) |
            Q(creator__email__icontains=search_query)
        )
    
    # 日付範囲の適用
    if date_from:
        requests = requests.filter(created_at__gte=date_from)
    
    if date_to:
        requests = requests.filter(created_at__lte=date_to)
    
    # 承認が必要なリクエストのフィルター
    needs_approval = request.GET.get('needs_approval')
    if needs_approval == 'true':
        # ユーザーの承認が必要なリクエストのIDを取得
        approval_request_ids = RequestApproval.objects.filter(
            approver=user,
            status='pending'
        ).values_list('request_id', flat=True)
        requests = requests.filter(id__in=approval_request_ids)
    
    # 割り当てられたリクエストのフィルター
    assigned_to_me = request.GET.get('assigned_to_me')
    if assigned_to_me == 'true':
        requests = requests.filter(assigned_to=user)
    
    # 作成者でのフィルター
    created_by_me = request.GET.get('created_by_me')
    if created_by_me == 'true':
        requests = requests.filter(creator=user)
    
    # 更新日時でソート（最新順）
    requests = requests.order_by('-updated_at')
    
    # 統計情報
    stats = {
        'total': requests.count(),
        'pending': requests.filter(status='pending').count(),
        'approved': requests.filter(status='approved').count(),
        'rejected': requests.filter(status='rejected').count(),
        'needs_approval': RequestApproval.objects.filter(approver=user, status='pending').count(),
    }
    
    context = {
        'requests': requests,
        'current_status': status,
        'current_priority': priority,
        'current_category': category,
        'current_direction': direction,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
        'needs_approval': needs_approval,
        'assigned_to_me': assigned_to_me,
        'created_by_me': created_by_me,
        'stats': stats,
        'title': _('Requests'),
    }
    
    return render(request, 'reqs/request_list.html', context)

@login_required
def request_detail(request, pk):
    """View for request details."""
    # Get the request object
    req = get_object_or_404(
        Request.objects.select_related('creator', 'assigned_to', 'company_from', 'company_to')
        .prefetch_related('approvals__approver', 'attachments__uploaded_by'),
        pk=pk
    )
    
    # Check if user has permission to view this request
    user = request.user
    company = user.company
    
    if company != req.company_from and company != req.company_to:
        messages.error(request, _('You do not have permission to view this request.'))
        return redirect('reqs:list')
    
    # Get approvals and attachments
    approvals = req.approvals.all().order_by('order')
    attachments = req.attachments.all().order_by('-created_at')
    
    # Check if the current user needs to approve this request
    needs_approval = req.is_pending_approval_from(user)
    
    # For handling approval actions
    if needs_approval and request.method == 'POST':
        approval_form = RequestApprovalForm(request.POST, instance=req.get_current_approval())
        if approval_form.is_valid():
            approval = approval_form.save(commit=False)
            approval.approved_at = timezone.now()
            approval.save()
            
            # Update request status based on approval
            if approval.status == 'approved':
                # Check if this was the last approval
                if not req.get_current_approval():
                    req.status = 'approved'
                    req.save()
                messages.success(request, _('Request approved successfully.'))
            else:  # 'rejected'
                req.status = 'rejected'
                req.save()
                messages.success(request, _('Request rejected.'))
            
            return redirect('reqs:detail', pk=pk)
    else:
        approval_form = RequestApprovalForm()
    
    # For adding attachments
    attachment_form = RequestAttachmentForm()
    
    context = {
        'request_obj': req,  # Using request_obj to avoid conflict with request
        'approvals': approvals,
        'attachments': attachments,
        'needs_approval': needs_approval,
        'approval_form': approval_form,
        'attachment_form': attachment_form,
        'title': req.title,
    }
    
    return render(request, 'reqs/request_detail.html', context)


@login_required
def request_create(request):
    """View for creating a new request."""
    user = request.user
    
    if not user.company:
        messages.error(request, _('You need to be associated with a company to create requests.'))
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = RequestForm(request.POST, user=user)
        approver_formset = ApproverFormSet(request.POST, prefix='approvers')
        
        if form.is_valid() and approver_formset.is_valid():
            # Save the request
            req = form.save(commit=False)
            req.creator = user
            req.company_from = user.company
            req.status = 'pending'  # Set initial status
            req.save()
            
            # Process approvers
            for i, approver_form in enumerate(approver_formset):
                if approver_form.cleaned_data and not approver_form.cleaned_data.get('DELETE', False):
                    approver_id = approver_form.cleaned_data.get('approver')
                    if approver_id:
                        # Create approval workflow entry
                        RequestApproval.objects.create(
                            request=req,
                            approver_id=approver_id,
                            status='pending',
                            order=i
                        )
            
            messages.success(request, _('Request created successfully.'))
            return redirect('reqs:detail', pk=req.pk)
    else:
        form = RequestForm(user=user)
        approver_formset = ApproverFormSet(prefix='approvers')
    
    context = {
        'form': form,
        'approver_formset': approver_formset,
        'title': _('Create Request'),
    }
    
    return render(request, 'reqs/request_form.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q
from django.forms import formset_factory

from .models import Request, RequestApproval, Attachment
from .forms import RequestForm, RequestApprovalForm, RequestAttachmentForm, ApproverForm, ApproverFormSet


@login_required
def request_create(request):
    """View for creating a new request."""
    user = request.user
    
    if not user.company:
        messages.error(request, _('You need to be associated with a company to create requests.'))
        return redirect('dashboard:home')
    
    # Initialize forms
    if request.method == 'POST':
        form = RequestForm(request.POST, user=user)
        
        # Form validation and saving
        if form.is_valid():
            # Save the request
            req = form.save()
            
            # Get target company to filter approvers
            company_to = req.company_to
            
            # Initialize approver formset with the target company
            approver_formset = ApproverFormSet(request.POST, prefix='approvers')
            
            # Validate each approver form with the target company
            valid_formset = True
            for form_index, approver_form in enumerate(approver_formset.forms):
                # Set the company for each form to update queryset
                approver_form.company_to = company_to
                # Manually update queryset
                approver_form.fields['approver'].queryset = user.__class__.objects.filter(
                    company=company_to, 
                    is_active=True
                ).exclude(role='user')
                
                # If individual form is not valid, mark the whole formset as invalid
                if not approver_form.is_valid():
                    valid_formset = False
            
            if approver_formset.is_valid() and valid_formset:
                # Process approvers
                for i, approver_form in enumerate(approver_formset):
                    if approver_form.cleaned_data and not approver_form.cleaned_data.get('DELETE', False):
                        approver_id = approver_form.cleaned_data.get('approver')
                        if approver_id:
                            # Create approval workflow entry
                            RequestApproval.objects.create(
                                request=req,
                                approver=approver_id,
                                status='pending',
                                order=i
                            )
                
                messages.success(request, _('Request created successfully.'))
                return redirect('reqs:detail', pk=req.pk)
            else:
                # Form was invalid, show error
                messages.error(request, _('Please correct the errors in the approver selection.'))
        else:
            # Request form was invalid
            messages.error(request, _('Please correct the errors in the form.'))
    else:
        # Initial form load
        form = RequestForm(user=user)
        approver_formset = ApproverFormSet(prefix='approvers')
    
    context = {
        'form': form,
        'approver_formset': approver_formset,
        'title': _('Create Request'),
    }
    
    return render(request, 'reqs/request_form.html', context)


@login_required
def request_edit(request, pk):
    """View for editing an existing request."""
    req = get_object_or_404(Request, pk=pk)
    user = request.user
    
    # Check permissions - only creator or assigned user from the same company can edit
    if user != req.creator and user != req.assigned_to and user.company != req.company_from:
        messages.error(request, _('You do not have permission to edit this request.'))
        return redirect('reqs:detail', pk=pk)
    
    # Only allow editing of draft or pending requests
    if req.status not in ['draft', 'pending']:
        messages.error(request, _('This request can no longer be edited.'))
        return redirect('reqs:detail', pk=pk)
    
    if request.method == 'POST':
        form = RequestForm(request.POST, instance=req, user=user)
        
        if form.is_valid():
            form.save()
            messages.success(request, _('Request updated successfully.'))
            return redirect('reqs:detail', pk=pk)
    else:
        form = RequestForm(instance=req, user=user)
    
    context = {
        'form': form,
        'request_obj': req,
        'is_edit': True,
        'title': _('Edit Request'),
    }
    
    return render(request, 'reqs/request_form.html', context)

@login_required
def request_approval(request, pk):
    """View for handling request approvals."""
    req = get_object_or_404(Request, pk=pk)
    user = request.user
    
    # Check if this user is an approver for this request
    approval = RequestApproval.objects.filter(
        request=req,
        approver=user,
        status='pending'
    ).first()
    
    if not approval:
        messages.error(request, _('You are not authorized to approve this request.'))
        return redirect('reqs:detail', pk=pk)
    
    if request.method == 'POST':
        form = RequestApprovalForm(request.POST, instance=approval)
        
        if form.is_valid():
            approval = form.save(commit=False)
            approval.approved_at = timezone.now()
            approval.save()
            
            # Update request status based on approval
            if approval.status == 'approved':
                # Check if this was the last approval
                if not req.get_current_approval():
                    req.status = 'approved'
                    req.save()
                messages.success(request, _('Request approved successfully.'))
            else:  # 'rejected'
                req.status = 'rejected'
                req.save()
                messages.success(request, _('Request rejected.'))
            
            return redirect('reqs:detail', pk=pk)
    else:
        form = RequestApprovalForm(instance=approval)
    
    context = {
        'form': form,
        'request_obj': req,
        'approval': approval,
        'title': _('Approve Request'),
    }
    
    return render(request, 'reqs/request_approval.html', context)


@login_required
def add_attachment(request, pk):
    """View for adding attachments to a request."""
    req = get_object_or_404(Request, pk=pk)
    user = request.user
    
    # Check permissions - users from either company can add attachments
    if user.company != req.company_from and user.company != req.company_to:
        messages.error(request, _('You do not have permission to add attachments to this request.'))
        return redirect('reqs:detail', pk=pk)
    
    if request.method == 'POST':
        form = RequestAttachmentForm(request.POST, request.FILES, request=req, user=user)
        
        if form.is_valid():
            attachment = form.save()
            
            if request.htmx:
                # Return partial template for HTMX request
                return render(request, 'reqs/partials/attachment_item.html', {
                    'attachment': attachment,
                    'request_obj': req,
                })
            
            messages.success(request, _('Attachment added successfully.'))
            return redirect('reqs:detail', pk=pk)
    
    # If it's not a POST request or form is invalid, redirect back to detail
    return redirect('reqs:detail', pk=pk)


@login_required
def delete_attachment(request, pk):
    """View for deleting an attachment."""
    attachment = get_object_or_404(Attachment, pk=pk)
    req = attachment.request
    user = request.user
    
    # Check permissions - only the uploader or an admin/manager from the same company can delete
    if (user != attachment.uploaded_by and 
        not user.is_admin and 
        not user.is_manager and
        user.company != attachment.uploaded_by.company):
        messages.error(request, _('You do not have permission to delete this attachment.'))
        return redirect('reqs:detail', pk=req.pk)
    
    if request.method == 'POST':
        attachment.delete()
        
        if request.htmx:
            return HttpResponse('', status=204)
        
        messages.success(request, _('Attachment deleted successfully.'))
    
    return redirect('reqs:detail', pk=req.pk)