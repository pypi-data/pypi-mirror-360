from rest_framework_simplejwt.tokens import AccessToken


class BearerToken(AccessToken):
    token_type = "Bearer"


class IDToken(AccessToken):
    token_type = "ID"
