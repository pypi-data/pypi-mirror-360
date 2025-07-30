"""App Settings"""

# Django
from django.conf import settings
from django.apps import AppConfig

class CorpTaxConfig(AppConfig):
    """App configuration for CorpTax"""
    
    name = 'corptax'
    verbose_name = "Corp Tax"
    
    def ready(self):
        """Ready method to initialize app settings"""
        # Ensure the app is loaded and settings are configured
        if not hasattr(settings, 'CORPTAX'):
            settings.CORPTAX = {
                'ACCOUNTED_ALLIANCE': False,
            }



