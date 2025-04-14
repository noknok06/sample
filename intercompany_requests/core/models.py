# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """カスタムユーザーモデル"""
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='employees', null=True)
    role = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.company})"

class Company(models.Model):
    """会社モデル"""
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=(
        ('active', 'アクティブ'),
        ('inactive', '非アクティブ'),
        ('pending', '保留中'),
    ), default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def active_requests(self):
        """進行中の要望数を返す"""
        return self.received_requests.exclude(status__in=['completed', 'rejected']).count()

class Request(models.Model):
    """要望モデル"""
    STATUS_CHOICES = (
        ('pending', '保留中'),
        ('reviewed', 'レビュー中'),
        ('approved', '承認済み'),
        ('completed', '完了'),
        ('rejected', '却下'),
    )
    
    PRIORITY_CHOICES = (
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    sender_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sent_requests')
    receiver_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='received_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    """要望へのコメントモデル"""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.request.title}"

class Attachment(models.Model):
    """要望の添付ファイルモデル"""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    name = models.CharField(max_length=100)
    size = models.IntegerField()  # byte単位
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Activity(models.Model):
    """要望の活動履歴モデル"""
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.action