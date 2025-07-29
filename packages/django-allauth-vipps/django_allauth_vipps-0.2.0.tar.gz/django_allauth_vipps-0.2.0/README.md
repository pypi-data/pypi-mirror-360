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
-   Allows customization of requested scopes.
-   Fully tested and documented for a "drop-in" experience.

## 1. Installation & Setup

### Step 1: Install the Package

```bash
pip install django-allauth-vipps
```
*(Or `poetry add django-allauth-vipps` if you use Poetry)*

### Step 2: Update `INSTALLED_APPS`

Add `vipps_auth` to your `INSTALLED_APPS` in your Django `settings.py`. It must be placed after the standard `allauth` apps.

```python
# settings.py

INSTALLED_APPS = [
    # ... other apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth

    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Add the Vipps provider app
    'vipps_auth',
]

# Required by allauth
SITE_ID = 1

# Ensure you have authentication backends configured
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

### Step 3: Configure the Provider

This package is configured using `django-allauth`'s standard `SOCIALACCOUNT_PROVIDERS` setting. This allows you to set your credentials, select the environment (test or production), and define what data you request from the user.

Add the following to your `settings.py`:

```python
# settings.py
import os

SOCIALACCOUNT_PROVIDERS = {
    'vipps': {
        # Method 1 (Recommended): Configure credentials directly in settings.
        # This is ideal for production and CI/CD environments.
        'APPS': [
            {
                'client_id': os.getenv('VIPPS_CLIENT_ID'),
                'secret': os.getenv('VIPPS_CLIENT_SECRET'),
                'key': '' # Not used by Vipps
            }
        ],

        # --- General Provider Settings ---

        # For production, this must be False. For development, set to True
        # to use the Vipps test API ([https://apitest.vipps.no](https://apitest.vipps.no)).
        'TEST_MODE': False,

        # This tells django-allauth to trust the email address received from Vipps.
        'VERIFIED_EMAIL': True,

        # (Recommended) Enforce that the login fails if Vipps has not
        # verified the user's email address on their end.
        'EMAIL_VERIFIED_REQUIRED': True,

        # Define the specific user data (scopes) you want to request.
        'SCOPE': [
            'openid',
            'name',
            'email',
            'phoneNumber',
        ],
    }
}
```
> **Important:** For credentials, choose **one** method. Either use the `APPS` key in `settings.py` (recommended) or create a `SocialApp` in the Django Admin as described in the `django-allauth` documentation. Using both for the same provider will cause an error.

### Step 4: Configure on Vipps Developer Portal

1.  Log in to the [Vipps MobilePay Developer Portal](https://portal.vippsmobilepay.com/).
2.  Navigate to the "Developer" section and get your credentials for a sales unit.
    * **Client ID** (goes into `VIPPS_CLIENT_ID` environment variable)
    * **Client Secret** (goes into `VIPPS_CLIENT_SECRET` environment variable)
3.  In the **"Redirect URIs"** section, add the URL that Vipps will redirect users back to.
    * **Standard Web Flow:** `https://yourdomain.com/accounts/vipps/login/callback/`
    * **API/SPA Flow:** This should be the URL of your *frontend* application that handles the final redirect, e.g., `https://my-react-app.com/auth/callback/vipps`

### Step 5: Run Database Migrations
```bash
python manage.py migrate
```

## 2. Usage

### For Traditional Django Websites

If you are using server-rendered templates, add a Vipps login button with the `provider_login_url` template tag.

**In your template (`login.html`):**
```html
{% load socialaccount %}

<h2>Login</h2>
<a href="{% provider_login_url 'vipps' %}">Log In with Vipps</a>
```

### For REST APIs (with `dj-rest-auth`)

This is the standard flow for Single-Page Applications (React, Vue, etc.).

In your project's `urls.py`, create a login view that uses the `VippsOAuth2Adapter`.

```python
# your_project/urls.py
from django.urls import path
from dj_rest_auth.registration.views import SocialLoginView
from vipps_auth.views import VippsOAuth2Adapter

# This view connects dj-rest-auth to our Vipps adapter.
# No client_class is needed unless you have advanced requirements.
class VippsLoginAPI(SocialLoginView):
    adapter_class = VippsOAuth2Adapter
    # This MUST match the redirect URI you set in the Vipps Portal for your frontend
    callback_url = "YOUR_FRONTEND_CALLBACK_URL" 

urlpatterns = [
    # ... your other urls
    path("api/v1/auth/vipps/", VippsLoginAPI.as_view(), name="vipps_login_api"),
]
```

## 3. Development & Testing

To work on this package locally:
1.  Clone the repository: `git clone https://github.com/danpejobo/django-allauth-vipps.git`
2.  Install dependencies: `poetry install`
3.  Activate the virtual environment: `poetry shell`
4.  Run the test suite: `poetry run pytest`