from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse

from reqs.models import Request
from .models import Comment
from .forms import CommentForm

@login_required
def add_comment(request, request_id):
    """リクエストにコメントを追加する"""
    req = get_object_or_404(Request, pk=request_id)
    
    # 所属企業のチェック - 関連企業のユーザーのみコメント可能
    user_company = request.user.company
    if user_company != req.company_from and user_company != req.company_to:
        messages.error(request, _('このリクエストにコメントする権限がありません。'))
        return redirect('reqs:detail', pk=request_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, request_obj=req, author=request.user)
        if form.is_valid():
            comment = form.save()
            
            if request.htmx:
                return render(request, 'comments/partials/comment_item.html', {
                    'comment': comment,
                    'request_obj': req,
                })
            
            messages.success(request, _('コメントが追加されました。'))
            return redirect('reqs:detail', pk=request_id)
    
    # POSTリクエストでなければ、リクエスト詳細ページにリダイレクト
    return redirect('reqs:detail', pk=request_id)

@login_required
def edit_comment(request, pk):
    """コメントを編集する"""
    comment = get_object_or_404(Comment, pk=pk)
    req = comment.request
    
    # 権限チェック - 作成者またはAdmin/Managerのみ編集可能
    if (request.user != comment.author and
        not request.user.is_admin and
        not request.user.is_manager):
        messages.error(request, _('このコメントを編集する権限がありません。'))
        return redirect('reqs:detail', pk=req.pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            
            if request.htmx:
                return render(request, 'comments/partials/comment_item.html', {
                    'comment': comment,
                    'request_obj': req,
                })
            
            messages.success(request, _('コメントが更新されました。'))
            return redirect('reqs:detail', pk=req.pk)
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form,
        'comment': comment,
        'request_obj': req,
    }
    
    if request.htmx:
        return render(request, 'comments/partials/comment_form.html', context)
    
    return render(request, 'comments/edit_comment.html', context)

@login_required
def delete_comment(request, pk):
    """コメントを削除する"""
    comment = get_object_or_404(Comment, pk=pk)
    req = comment.request
    
    # 権限チェック - 作成者またはAdmin/Managerのみ削除可能
    if (request.user != comment.author and
        not request.user.is_admin and
        not request.user.is_manager):
        messages.error(request, _('このコメントを削除する権限がありません。'))
        return redirect('reqs:detail', pk=req.pk)
    
    if request.method == 'POST':
        comment.delete()
        
        if request.htmx:
            return HttpResponse('', status=204)
        
        messages.success(request, _('コメントが削除されました。'))
        return redirect('reqs:detail', pk=req.pk)
    
    context = {
        'comment': comment,
        'request_obj': req,
    }
    
    if request.htmx:
        return render(request, 'comments/partials/delete_confirm.html', context)
    
    return render(request, 'comments/delete_comment.html', context)