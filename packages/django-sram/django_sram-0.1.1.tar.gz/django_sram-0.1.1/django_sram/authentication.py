from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication


class OAUTH2ProxyStatelessAuthentication(JWTStatelessUserAuthentication):
    """OAuth2 Proxy uses the HTT_X_FORWARDED_ACCESS_TOKEN header directly"""

    def get_raw_token(self, header: bytes) -> bytes:
        return header
