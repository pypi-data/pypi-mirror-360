# vipps_auth/provider.py

from allauth.account.adapter import get_adapter
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class VippsAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get('name', super().to_str())


class VippsProvider(OAuth2Provider):
    id = 'vipps'
    name = 'Vipps'
    account_class = VippsAccount

    def get_base_url(self):
        """Get the base URL from settings, defaulting to production."""
        settings = self.get_settings()
        is_test_mode = settings.get('TEST_MODE', False)
        if is_test_mode:
            return "https://apitest.vipps.no"
        return "https://api.vipps.no"

    def get_default_scope(self):
        """Get scopes, with a hardcoded default."""
        scope = ["openid", "name", "email", "phoneNumber"]
        settings = self.get_settings()
        if 'SCOPE' in settings:
            scope = settings['SCOPE']
        return scope

    def get_access_token_url(self, request):
        return f"{self.get_base_url()}/access-management-1.0/access/oauth2/token"

    def get_authorize_url(self, request):
        return f"{self.get_base_url()}/access-management-1.0/access/oauth2/auth"

    def get_profile_url(self, request):
        return f"{self.get_base_url()}/vipps-userinfo-api/userinfo"

    def extract_uid(self, data):
        return str(data['sub'])

    def extract_common_fields(self, data):
        return {
            'email': data.get('email'),
            'first_name': data.get('given_name'),
            'last_name': data.get('family_name'),
        }

    def sociallogin_from_response(self, request, response):
        """Handle the login response, checking for verified email based on settings."""
        settings = self.get_settings()
        email_verified_required = settings.get('EMAIL_VERIFIED_REQUIRED', True)

        if email_verified_required:
            if not response.get('email_verified', False):
                get_adapter().error("Login cancelled: Email from Vipps is not verified.")

        return super().sociallogin_from_response(request, response)