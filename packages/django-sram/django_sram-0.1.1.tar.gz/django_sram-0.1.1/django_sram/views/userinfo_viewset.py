from django.http import HttpRequest
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django_sram.user import TokenUser


class UserInfo(mixins.ListModelMixin, viewsets.ViewSet):
    permission_classes = [AllowAny]  # endpoint for checking if you are logged in

    def list(self, request: HttpRequest, *args, **kwargs):
        user: TokenUser = request.user
        try:
            data = {
                "uid": user.id,
                "name": getattr(user, "name"),
                "preferred_username": getattr(user, "preferred_username"),
                "given_name": getattr(user, "given_name"),
                "family_name": getattr(user, "family_name"),
                "email": getattr(user, "email"),
                "email_verified": getattr(user, "email_verified"),
                "eduperson_entitlement": getattr(user, "eduperson_entitlement"),
                "eduperson_unique_id": getattr(user, "eduperson_unique_id"),
                "token_type": getattr(user, "typ"),
            }

            res_status = status.HTTP_200_OK
        except AttributeError:
            data = {
                "detail": "token auth failed",
                "headers": request.headers,
            }
            res_status = status.HTTP_401_UNAUTHORIZED

        return Response(data, status=res_status)
