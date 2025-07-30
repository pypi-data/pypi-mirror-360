from rest_framework_simplejwt import models


class TokenUser(models.TokenUser):
    """
    Placeholder Class

    Implementation see: https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/models.py
    """

    def is_member_of_group_in_co(self, org: str, co: str, group: str) -> bool:
        """returns the user is member of group in given collaborative organisation"""
        match = f"urn:mace:surf.nl:sram:group:{org}:{co}:{group}"
        entitlements = self.token.get("eduperson_entitlement")
        return match in entitlements
