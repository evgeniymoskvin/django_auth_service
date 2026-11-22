
"""URL-маршруты проекта django_auth_service."""

from django.contrib import admin
from django.urls import path, include

from identity.kerberos.oidc import KerberosAuthorizationView


urlpatterns = [
    path("admin/", admin.site.urls),

    # Собственный обработчик OIDC Authorization Endpoint.
    path(
        "o/authorize/",
        KerberosAuthorizationView.as_view(),
        name="kerberos_authorize",
    ),

    # Остальные стандартные маршруты OAuth Toolkit.
    path(
        "o/",
        include("oauth2_provider.urls", namespace="oauth2_provider"),
    ),

    path("", include("login.urls")),
    path("accounts/", include("accounts.urls")),
]
