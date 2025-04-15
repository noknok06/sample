# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Company, Request, Comment, Attachment
from .models import Request, Comment, Company, User

class CustomUserCreationForm(UserCreationForm):
    """カスタムユーザー作成フォーム"""
    company_name = forms.CharField(max_length=100, required=True)
    role = forms.CharField(max_length=100, required=False)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    terms = forms.BooleanField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        # ユーザーを作成
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        # 会社の作成または取得
        company_name = self.cleaned_data['company_name']
        company, created = Company.objects.get_or_create(
            name=company_name,
            defaults={
                'industry': 'その他',
                'email': user.email,
                'status': 'active'
            }
        )
        
        # ユーザーに会社を割り当て
        user.company = company
        user.role = self.cleaned_data.get('role', '')
        
        if commit:
            user.save()
        
        return user

    def clean_terms(self):
        """利用規約への同意を確認"""
        terms = self.cleaned_data.get('terms')
        if not terms:
            raise forms.ValidationError("利用規約に同意する必要があります。")
        return terms
    
class RequestForm(forms.ModelForm):
    """要望登録・編集フォーム"""
    attachments = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': False}),  # もしくはこの行ごと削除
        label='添付ファイル'
    )
    
    class Meta:
        model = Request
        fields = ['receiver_company', 'title', 'description', 'category', 'priority', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
class CommentForm(forms.ModelForm):
    """コメント投稿フォーム"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'コメントを入力してください'}),
        }

class CompanyForm(forms.ModelForm):
    """会社情報登録・編集フォーム"""
    class Meta:
        model = Company
        fields = ['name', 'industry', 'email', 'phone', 'address', 'status']
        
class UserProfileForm(forms.ModelForm):
    """ユーザープロフィール編集フォーム"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role']