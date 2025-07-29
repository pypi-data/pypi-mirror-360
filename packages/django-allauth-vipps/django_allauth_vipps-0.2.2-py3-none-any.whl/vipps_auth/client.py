# vipps_auth/client.py

from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class VippsOAuth2Client(OAuth2Client):
    """
    Custom client to handle incompatibilities between dj-rest-auth and
    newer versions of django-allauth. It correctly sets basic_auth
    and manages the __init__ signature.
    """
    def __init__(
        self,
        request,
        consumer_key,
        consumer_secret,
        access_token_method,
        access_token_url,
        callback_url,
        scope,  # <-- Accept the 'scope' argument to be compatible with the caller
        **kwargs
    ):
        kwargs['basic_auth'] = True
        
        # Call the parent class's __init__ method, but WITHOUT the `scope`
        # argument, as it is no longer accepted.
        super().__init__(
            request,
            consumer_key,
            consumer_secret,
            access_token_method,
            access_token_url,
            callback_url,
            **kwargs  # Pass the remaining kwargs
        )