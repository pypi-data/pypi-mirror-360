from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django_sram.views.userinfo_viewset import UserInfo

router = DefaultRouter()
router.register(r"userinfo", UserInfo, "userinfo")

urlpatterns = [
    path("", include(router.urls)),
]
