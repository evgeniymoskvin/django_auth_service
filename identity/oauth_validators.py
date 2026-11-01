
from oauth2_provider.oauth2_validators import OAuth2Validator

from .models import UserIdentity
from .access import is_employee_allowed


class CustomOAuth2Validator(OAuth2Validator):

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        if not super().validate_code(
            client_id, code, client, request, *args, **kwargs
        ):
            return False

        return is_employee_allowed(request.user)

    def validate_refresh_token(
        self, refresh_token, client, request, *args, **kwargs
    ):
        if not super().validate_refresh_token(
            refresh_token, client, request, *args, **kwargs
        ):
            return False

        return is_employee_allowed(request.user)

    def get_claim_dict(self, request):
        claims = super().get_claim_dict(request)

        identity = UserIdentity.objects.get(user=request.user)
        claims["sub"] = str(identity.subject)

        return claims
