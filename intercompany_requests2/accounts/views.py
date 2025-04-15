from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse

from .forms import UserProfileForm, UserRoleForm

User = get_user_model()

@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated.'))
            
            if request.htmx:
                return HttpResponse(
                    status=204, 
                    headers={'HX-Trigger': 'profileUpdated'}
                )
            
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'form': form,
        'user': user
    }
    
    if request.htmx:
        return render(request, 'accounts/partials/profile_form.html', context)
    
    return render(request, 'accounts/profile.html', context)

@login_required
def company_users_view(request):
    """View for listing users in the current user's company"""
    if not request.user.company:
        messages.warning(request, _('You are not associated with any company yet.'))
        return redirect('dashboard:home')
    
    # Only admins or managers can access this page
    if not (request.user.is_admin or request.user.is_manager):
        messages.error(request, _('You do not have permission to access this page.'))
        return redirect('dashboard:home')
    
    company = request.user.company
    users = User.objects.filter(company=company).order_by('first_name', 'last_name')
    
    context = {
        'company': company,
        'users': users,
    }
    
    if request.htmx:
        return render(request, 'accounts/partials/users_list.html', context)
    
    return render(request, 'accounts/company_users.html', context)

@login_required
def update_user_role(request, pk):
    """Update user role (admin only)"""
    if not request.user.is_admin:
        messages.error(request, _('You do not have permission to perform this action.'))
        return redirect('accounts:company_users')
    
    user = get_object_or_404(User, pk=pk, company=request.user.company)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('User role has been updated.'))
            
            if request.htmx:
                return HttpResponse(
                    status=204, 
                    headers={'HX-Trigger': 'userRoleUpdated'}
                )
                
            return redirect('accounts:company_users')
    else:
        form = UserRoleForm(instance=user)
    
    context = {
        'form': form,
        'user_obj': user
    }
    
    if request.htmx:
        return render(request, 'accounts/partials/role_form.html', context)
    
    return render(request, 'accounts/update_role.html', context)