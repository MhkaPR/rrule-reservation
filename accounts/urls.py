from django.urls import path, include
from rest_framework import routers

from accounts.views import AuthenticationViewSet

router = routers.DefaultRouter()
router.register("authenticate", AuthenticationViewSet, basename="authenticate")
urlpatterns = [
    path("otp/", include("phone_verify.urls")),
]

urlpatterns += router.urls