from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Company, CompanyConnection

class CompanyForm(forms.ModelForm):
    """Form for creating and updating company information"""
    class Meta:
        model = Company
        fields = [
            'name', 'industry', 'address', 'phone', 
            'email', 'website', 'description', 'logo'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'logo': forms.FileInput(attrs={'class': 'hidden'}),
        }

class CompanyConnectionForm(forms.ModelForm):
    """Form for creating company connections"""
    class Meta:
        model = CompanyConnection
        fields = ['company_to']
    
    def __init__(self, *args, **kwargs):
        # Get the current company to exclude it from the choices
        current_company = kwargs.pop('current_company', None)
        super().__init__(*args, **kwargs)
        
        # Exclude current company and already connected companies
        if current_company:
            # Get IDs of companies already connected to (including pending)
            connected_ids = CompanyConnection.objects.filter(
                company_from=current_company
            ).values_list('company_to_id', flat=True)
            
            # Also exclude companies that have sent a connection request
            incoming_ids = CompanyConnection.objects.filter(
                company_to=current_company
            ).values_list('company_from_id', flat=True)
            
            # Combine all excluded IDs
            excluded_ids = list(connected_ids) + list(incoming_ids) + [current_company.id]
            
            # Filter queryset
            self.fields['company_to'].queryset = Company.objects.exclude(
                id__in=excluded_ids
            ).filter(is_active=True)

class CompanyInviteForm(forms.Form):
    """Form for inviting a user to join a company"""
    email = forms.EmailField(
        label=_('Email Address'),
        help_text=_('Enter the email address of the person you want to invite.')
    )
    message = forms.CharField(
        label=_('Invitation Message'),
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text=_('You can include a personalized message in the invitation email.')
    )

class CompanyJoinForm(forms.Form):
    """Form for joining a company using an invitation code"""
    invitation_code = forms.UUIDField(
        label=_('Invitation Code'),
        help_text=_('Enter the invitation code you received.')
    )