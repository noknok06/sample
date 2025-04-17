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

from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Company, CompanyConnection

class CompanyConnectionForm(forms.Form):
    """企業間接続のためのフォーム"""
    company_to = forms.ModelChoiceField(
        queryset=Company.objects.none(),  # 動的に設定されるクエリセット
        label=_('接続先企業'),
        empty_label=_('企業を選択'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        # 現在の企業を取得（デフォルトはNone）
        current_company = kwargs.pop('current_company', None)
        super().__init__(*args, **kwargs)
        
        if current_company:
            # 既に接続済みまたは接続リクエスト中の企業のIDを取得
            connected_ids = CompanyConnection.objects.filter(
                Q(company_from=current_company) | Q(company_to=current_company),
                Q(status__in=['pending', 'accepted'])
            ).values_list('company_from_id', 'company_to_id')
            
            # 接続済みの企業IDをフラットなセットに変換
            flat_connected_ids = set(id for ids in connected_ids for id in ids)
            
            # 現在の企業自体も除外
            flat_connected_ids.add(current_company.id)
            
            # 接続済みの企業を除外し、有効な企業のみを選択可能に
            self.fields['company_to'].queryset = Company.objects.exclude(
                id__in=flat_connected_ids
            ).filter(
                is_active=True
            )
        else:
            # 現在の企業が指定されていない場合は、有効な企業をすべて表示
            self.fields['company_to'].queryset = Company.objects.filter(is_active=True)
            
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