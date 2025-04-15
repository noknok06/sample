from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReqsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reqs'
    verbose_name = _('Requests')

    def ready(self):
        import reqs.signals