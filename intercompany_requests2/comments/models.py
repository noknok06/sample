from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Comment(models.Model):
    """Model for storing comments on requests."""
    request = models.ForeignKey(
        'reqs.Request',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('request')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('author')
    )
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.email} on {self.request.title}'