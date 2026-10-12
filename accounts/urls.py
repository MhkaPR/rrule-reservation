from django.urls import path
from rest_framework import routers

from accounts.views import AuthenticationViewSet

router = routers.DefaultRouter()
router.register("authenticate", AuthenticationViewSet, basename="authenticate")
urlpatterns = []