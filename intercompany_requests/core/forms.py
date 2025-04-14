# forms.py
from django import forms
from .models import Request, Comment, Company, User

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