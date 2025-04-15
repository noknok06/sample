from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from companies.models import Company

User = get_user_model()


class Request(models.Model):
    """Model for managing requests between companies."""
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))
    
    CATEGORY_CHOICES = (
        ('general', _('General')),
        ('technical', _('Technical')),
        ('business', _('Business')),
        ('support', _('Support')),
        ('other', _('Other')),
    )
    category = models.CharField(
        _('category'),
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general'
    )
    
    PRIORITY_CHOICES = (
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    
    deadline = models.DateField(_('deadline'), null=True, blank=True)
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('review', _('In Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Relationships
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_requests',
        verbose_name=_('creator')
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_requests',
        null=True,
        blank=True,
        verbose_name=_('assigned to')
    )
    company_from = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='outgoing_requests',
        verbose_name=_('from company')
    )
    company_to = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='incoming_requests',
        verbose_name=_('to company')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('request')
        verbose_name_plural = _('requests')
        ordering = ['-updated_at']

    def __str__(self):
        return self.title
    
    def get_current_approval(self):
        """Get the current approval in the workflow."""
        pending_approvals = self.approvals.filter(status='pending').order_by('order')
        if pending_approvals.exists():
            return pending_approvals.first()
        return None
    
    def is_pending_approval_from(self, user):
        """Check if the request is pending approval from the specified user."""
        current_approval = self.get_current_approval()
        if current_approval and current_approval.approver == user:
            return True
        return False
    
    def get_completed_approvals(self):
        """Get all completed approvals for this request."""
        return self.approvals.filter(status__in=['approved', 'rejected']).order_by('order')
    
    def get_next_approver(self):
        """Get the next approver in the workflow."""
        current_approval = self.get_current_approval()
        if current_approval:
            return current_approval.approver
        return None


class RequestApproval(models.Model):
    """Model for managing approval workflow for requests."""
    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name='approvals',
        verbose_name=_('request')
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='request_approvals',
        verbose_name=_('approver')
    )
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    order = models.PositiveIntegerField(_('order'), default=0)
    comment = models.TextField(_('comment'), blank=True)
    approved_at = models.DateTimeField(_('approved at'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('request approval')
        verbose_name_plural = _('request approvals')
        ordering = ['request', 'order']
        unique_together = ['request', 'approver', 'order']

    def __str__(self):
        return f"{self.request.title} - {self.approver.email} ({self.get_status_display()})"


class Attachment(models.Model):
    """Model for storing attachments related to requests."""
    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('request')
    )
    file = models.FileField(_('file'), upload_to='attachments/')
    filename = models.CharField(_('filename'), max_length=255)
    file_type = models.CharField(_('file type'), max_length=100)
    file_size = models.PositiveIntegerField(_('file size'))
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_attachments',
        verbose_name=_('uploaded by')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')
        ordering = ['-created_at']

    def __str__(self):
        return self.filename