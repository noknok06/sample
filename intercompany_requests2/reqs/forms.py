from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Request, RequestApproval, Attachment

User = get_user_model()


class RequestForm(forms.ModelForm):
    """Form for creating and updating requests."""
    
    class Meta:
        model = Request
        fields = [
            'title', 'description', 'category', 'priority', 
            'deadline', 'company_to'
        ]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter company_to choices to show only connected companies
        if self.user and self.user.company:
            from companies.models import CompanyConnection
            connected_companies = CompanyConnection.objects.filter(
                company_from=self.user.company,
                status='accepted'
            ).values_list('company_to_id', flat=True)
            
            self.fields['company_to'].queryset = self.fields['company_to'].queryset.filter(
                id__in=connected_companies
            )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.user and not instance.pk:  # Only set these on creation
            instance.creator = self.user
            instance.company_from = self.user.company
        
        if commit:
            instance.save()
        
        return instance


class RequestApprovalForm(forms.ModelForm):
    """Form for approving or rejecting requests."""
    
    class Meta:
        model = RequestApproval
        fields = ['comment', 'status']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
            'status': forms.RadioSelect(choices=(
                ('approved', _('承認')),
                ('rejected', _('却下')),
            ))
        }


class RequestAttachmentForm(forms.ModelForm):
    """Form for adding attachments to requests."""
    
    class Meta:
        model = Attachment
        fields = ['file']
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.request:
            instance.request = self.request
        
        if self.user:
            instance.uploaded_by = self.user
        
        # Set file metadata
        file = self.cleaned_data['file']
        instance.filename = file.name
        instance.file_type = file.content_type
        instance.file_size = file.size
        
        if commit:
            instance.save()
        
        return instance


class ApproverForm(forms.Form):
    """Individual approver selection form."""
    approver = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label=_('承認者'),
        widget=forms.Select(attrs={'class': 'select-approver'})
    )
    order = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=0
    )
    
    def __init__(self, *args, **kwargs):
        self.company_to = kwargs.pop('company_to', None)
        super().__init__(*args, **kwargs)
        
        # Update approver choices based on target company
        if self.company_to:
            self.fields['approver'].queryset = User.objects.filter(
                company=self.company_to, 
                is_active=True
            ).exclude(role='user')  # Limit to admin/manager roles


ApproverFormSet = forms.formset_factory(
    form=ApproverForm,
    extra=1,
    can_delete=True
)