from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CompaniesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'companies'
    verbose_name = _('Companies')

    def ready(self):
        import companies.signals