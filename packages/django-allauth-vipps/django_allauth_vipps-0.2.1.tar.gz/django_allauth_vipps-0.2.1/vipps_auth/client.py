# vipps_auth/client.py

from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class VippsOAuth2Client(OAuth2Client):
    """
    Custom client to force the 'client_secret_basic' authentication method,
    which sends credentials in the Authorization header. This is required
    by Vipps when the client is configured for this method, which is the 
    default setting in vipps.
    """
    def __init__(self, *args, **kwargs):
        # This flag tells allauth to use HTTP Basic Auth.
        kwargs['basic_auth'] = True
        super().__init__(*args, **kwargs)