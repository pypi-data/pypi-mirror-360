# Django SRAM

![Build status](https://gitlab.com/astron-sdc/django_sram/badges/main/pipeline.svg)
![Test coverage](https://gitlab.com/astron-sdc/django_sram/badges/main/coverage.svg)
<!-- ![Latest release](https://gitlab.com/astron-sdc/django_sram/badges/main/release.svg) -->

SURF Research Access Management integration for Django

## Installation

Add django_sram and django-filter to requirements.txt

```
pip install django-sram django-filter
```

## Integration in Django project

To use this in a django application (assuming usage of keycloack and oauth2-proxy):

### settings.py:

#### Add the following apps to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    "my_client_app",
    "django_sram",
    "rest_framework" # Not strictly required, but prevents TemplateDoesNotExist errors
]
```

#### Configure REST_FRAMEWORK, SIMPLE_JWT, CSRF, Session cookie name:

```python
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "django_sram.authentication.UpsertJWTAuthentication",  # <-- use this to allow creation and updating of Django Users
        "rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication",
        # assumes header is of format `Bearer <JWT>`
        "django_sram.authentication.OAUTH2ProxyStatelessAuthentication",  # assumes header is of format `<JWT>`
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ALGORITHM": "RS256",
    # using `eduperson_unique_id` from SRAM insdead of `sub` from Keycloak
    "USER_ID_CLAIM": "eduperson_unique_id",
    "TOKEN_TYPE_CLAIM": "typ",  # Keycloak specific token type claim
    # Specific header set by oauth2 proxy
    # "AUTH_HEADER_NAME": "HTTP_X_FORWARDED_ACCESS_TOKEN",  # Use this to get the access/bearer token
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",  # default; Oauth2 Proxy uses ID token here
    # Custom token and TokenUser classes to parse claims
    "AUTH_TOKEN_CLASSES": [
        "django_sram.token.IDToken",
        "django_sram.token.BearerToken",
    ],
    "TOKEN_USER_CLASS": "django_sram.user.TokenUser",
    "JWK_URL": os.environ.get("OAUTH2_JWK_URL", ""),
}

SESSION_COOKIE_NAME = "my_client_app-sessionid"
CSRF_COOKIE_NAME = "my_client_app-csrftoken"
CSRF_TRUSTED_ORIGINS = [
    ("http://" if ("localhost" in host) else "https://") + host
    for host in ALLOWED_HOSTS
]

```

#### Expose userinfo endpoint in urls.py:


```python
from django_sram.views.userinfo_viewset import UserInfo

urlpatterns = [
    path('userinfo', # Add this route to skip_auth_routes of oauth2proxy config: "GET=^/userinfo"
        UserInfo.as_view({'get': 'list'}),
        name='userinfo'
    ),
]
```


## Development

### Development environment

To setup and activte the develop environment run ```source ./setup.sh``` from within the source directory.

If PyCharm is used, this only needs to be done once.
Afterward the Python virtual env can be setup within PyCharm.

### Contributing
To contribute, please create a feature branch and a "Draft" merge request.
Upon completion, the merge request should be marked as ready and a reviewer
should be assigned.

Verify your changes locally and be sure to add tests. Verifying local
changes is done through `tox`.

```pip install tox```

With tox the same jobs as run on the CI/CD pipeline can be ran. These
include unit tests and linting.

```tox```

To automatically apply most suggested linting changes execute:

```tox -e format```

## License
This project is licensed under the Apache License Version 2.0
