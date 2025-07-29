# vipps_auth/views.py

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from .provider import VippsProvider
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
import requests

class VippsOAuth2Adapter(OAuth2Adapter):
    provider_id = VippsProvider.id
    client_class = OAuth2Client

    # Add these properties back for dj-rest-auth compatibility.
    # They dynamically delegate the URL retrieval to the provider.
    @property
    def access_token_url(self):
        return self.get_provider().get_access_token_url(self.request)

    @property
    def authorize_url(self):
        return self.get_provider().get_authorize_url(self.request)

    @property
    def profile_url(self):
        return self.get_provider().get_profile_url(self.request)

    def complete_login(self, request, app, token, **kwargs):
        """Fetch user info from Vipps and return a populated SocialLogin."""
        # Use the property we just defined
        profile_url = self.profile_url
        headers = {"Authorization": f"Bearer {token.token}"}

        resp = requests.get(profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()

        return self.get_provider().sociallogin_from_response(request, extra_data)


vipps_login = OAuth2LoginView.adapter_view(VippsOAuth2Adapter)
vipps_callback = OAuth2CallbackView.adapter_view(VippsOAuth2Adapter)