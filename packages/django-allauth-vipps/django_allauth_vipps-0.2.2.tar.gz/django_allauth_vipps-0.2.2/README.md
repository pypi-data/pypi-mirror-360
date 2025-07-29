# Django Allauth Vipps Provider

[![PyPI version](https://badge.fury.io/py/django-allauth-vipps.svg)](https://pypi.org/project/django-allauth-vipps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD Tests](https://github.com/danpejobo/django-allauth-vipps/actions/workflows/ci.yml/badge.svg)](https://github.com/danpejobo/django-allauth-vipps/actions/workflows/ci.yml)

A complete `django-allauth` provider for Vipps Login, supporting both traditional web and modern API (`dj-rest-auth`) authentication flows.

This package provides a configurable, reusable Django app that allows users to sign in to your project using their Vipps account, making it easy to integrate Norway's most popular payment and identity solution.

## Features

-   Integrates seamlessly with `django-allauth`'s social account framework.
-   Supports API-first authentication flows via `dj-rest-auth`.
-   Configurable for both Vipps Test and Production environments via standard settings.
-   Correctly handles Vipps' required `client_secret_basic` authentication method for REST APIs.
-   Fully tested and documented for a "drop-in" experience.

## 1. Installation & Setup

### Step 1: Install the Package

```bash
pip install django-allauth-vipps
```

*(Or `poetry add django-allauth-vipps` if you use Poetry)*

### Step 2: Update `INSTALLED_APPS`

Add `vipps_auth` to your `INSTALLED_APPS` in your Django `settings.py`.

```python
# settings.py

INSTALLED_APPS = [
    # ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'vipps_auth',
]

SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

### Step 3: Configure the Provider

Configure the provider using `django-allauth`'s standard `SOCIALACCOUNT_PROVIDERS` setting in your `settings.py`.

```python
# settings.py
import os

SOCIALACCOUNT_PROVIDERS = {
    'vipps': {
        # Configure credentials using environment variables.
        'APPS': [
            {
                'client_id': os.getenv('VIPPS_CLIENT_ID'),
                'secret': os.getenv('VIPPS_CLIENT_SECRET'),
                'key': ''
            }
        ],

        # --- General Provider Settings ---
        'TEST_MODE': False, # Set to True for development/testing
        'VERIFIED_EMAIL': True,
        'EMAIL_VERIFIED_REQUIRED': True,
        'SCOPE': [
            'openid',
            'name',
            'email',
            'phoneNumber',
        ],
    }
}
```
> **Important:** For credentials, either use the `APPS` key in `settings.py` (recommended) or create a `SocialApp` in the Django Admin. Using both for the same provider will cause an error.

### Step 4: Configure on Vipps Developer Portal

1. Log in to the [Vipps MobilePay Developer Portal](https://portal.vippsmobilepay.com/).
2. Get your **Client ID** and **Client Secret**.
3. Set the **Token endpoint authentication method** to **`client_secret_basic`**.
4. Add your **Redirect URI** (`https://yourdomain.com/accounts/vipps/login/callback/` for web flows, or your frontend URL for API flows).

### Step 5: Run Migrations

```bash
python manage.py migrate
```

## 2. Usage

### For Traditional Django Websites

Use the `provider_login_url` template tag.
```html
{% load socialaccount %}
<a href="{% provider_login_url 'vipps' %}">Log In with Vipps</a>
```

### For REST APIs (with `dj-rest-auth`)

When using `dj-rest-auth`, you must use the custom `VippsOAuth2Client` provided by this package to ensure the correct authentication method (`client_secret_basic`) is used.

In your project's `urls.py`, create your login view like this:

```python
# your_project/urls.py
from django.urls import path
from dj_rest_auth.registration.views import SocialLoginView
from vipps_auth.views import VippsOAuth2Adapter
from vipps_auth.client import VippsOAuth2Client # <-- Import the custom client

# This view connects dj-rest-auth to our Vipps adapter
class VippsLoginAPI(SocialLoginView):
    adapter_class = VippsOAuth2Adapter
    client_class = VippsOAuth2Client  # <-- Use the custom client here
    callback_url = "YOUR_FRONTEND_CALLBACK_URL" 

urlpatterns = [
    # ... your other urls
    path("api/v1/auth/vipps/", VippsLoginAPI.as_view(), name="vipps_login_api"),
]