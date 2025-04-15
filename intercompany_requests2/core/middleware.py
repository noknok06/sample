from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CompanyRequiredMiddleware:
    """
    Middleware to ensure users are associated with a company.
    Redirects them to join a company if they don't have one.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Define URLs that don't require company association
        self.exempt_urls = [
            '/accounts/login/',
            '/accounts/signup/',
            '/accounts/logout/',
            '/accounts/password/reset/',
            '/companies/join/',
            '/admin/',
        ]
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return None
        
        # Skip for exempt URLs
        path = request.path_info
        if any(path.startswith(url) for url in self.exempt_urls):
            return None
        
        # If user doesn't have a company, redirect to join page
        if not request.user.company and not request.user.is_superuser:
            messages.warning(
                request,
                _('You need to join a company to access this feature.')
            )
            return redirect('companies:join')
        
        return None

class UserActivityMiddleware:
    """
    Middleware to track user's last active time.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Update last activity for authenticated users
        if request.user.is_authenticated:
            # Only update once every 15 minutes to reduce database writes
            should_update = True
            if hasattr(request.user, 'last_login') and request.user.last_login:
                # Check if it's been more than 15 minutes since last update
                time_since_update = timezone.now() - request.user.last_login
                if time_since_update.total_seconds() < 900:  # 15 minutes = 900 seconds
                    should_update = False
            
            if should_update:
                User.objects.filter(pk=request.user.pk).update(
                    last_login=timezone.now()
                )
        
        return response