from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Comment

class CommentForm(forms.ModelForm):
    """リクエストに対するコメントを作成するフォーム"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': _('コメントを入力してください')}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request_obj = kwargs.pop('request_obj', None)
        self.author = kwargs.pop('author', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.request_obj:
            instance.request = self.request_obj
        
        if self.author:
            instance.author = self.author
        
        if commit:
            instance.save()
        
        return instance