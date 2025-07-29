# vipps_auth/apps.py

from django.apps import AppConfig

class VippsAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vipps_auth'
    verbose_name = "Vipps Auth Provider"

    def ready(self):
        """
        Register the provider with django-allauth when the app is ready.
        """
        from allauth.socialaccount import providers
        from .provider import VippsProvider

        providers.registry.register(VippsProvider)