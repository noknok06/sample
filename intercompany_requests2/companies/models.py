from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class Company(models.Model):
    """Company model to store information about organizations"""
    name = models.CharField(_('company name'), max_length=255)
    industry = models.CharField(_('industry'), max_length=100, blank=True)
    address = models.TextField(_('address'), blank=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    email = models.EmailField(_('email'), blank=True)
    website = models.URLField(_('website'), blank=True)
    description = models.TextField(_('description'), blank=True)
    logo = models.ImageField(
        _('logo'),
        upload_to='company_logos/',
        blank=True,
        null=True
    )
    invitation_code = models.UUIDField(
        _('invitation code'),
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_admin_users(self):
        """Get all admin users for this company"""
        return self.users.filter(role='admin')
    
    def get_manager_users(self):
        """Get all manager users for this company"""
        return self.users.filter(role='manager')
    
    def get_regular_users(self):
        """Get all regular users for this company"""
        return self.users.filter(role='user')
    
    def get_active_users_count(self):
        """Get count of active users"""
        return self.users.filter(is_active=True).count()

class CompanyConnection(models.Model):
    """Model to store connections between companies"""
    company_from = models.ForeignKey(
        Company,
        related_name='outgoing_connections',
        on_delete=models.CASCADE,
        verbose_name=_('from company')
    )
    company_to = models.ForeignKey(
        Company,
        related_name='incoming_connections',
        on_delete=models.CASCADE,
        verbose_name=_('to company')
    )
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('company connection')
        verbose_name_plural = _('company connections')
        unique_together = ('company_from', 'company_to')

    def __str__(self):
        return f"{self.company_from} → {self.company_to} ({self.get_status_display()})"