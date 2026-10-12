import logging

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from phone_verify.services import send_security_code_and_generate_session_token
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet

from accounts.models import User
from accounts.serializers import SendOtpSerializer, UserSerializer
from phone_verify import serializers as phone_serializers
from accounts.utils import get_client_ip

logger = logging.getLogger(__name__)


class AuthenticationViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key=get_client_ip, rate="1/2m", block=True))
    @action(detail=False, methods=["post"], url_path="send-otp", serializer_class=SendOtpSerializer)
    def send_otp(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]

        try:
            session_token = send_security_code_and_generate_session_token(phone)
            return Response({"session_token": session_token}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("sending sms failed: %s", e, exc_info=True)
            return Response({"error": "sending sms failed!"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="verify", serializer_class=phone_serializers.SMSVerificationSerializer)
    def verify_and_register(self, request):
        phone_serializer = self.get_serializer(data=request.data)
        phone_serializer.is_valid(raise_exception=True)
        phone = phone_serializer.validated_data["phone_number"]

        user, created = User.objects.get_or_create(phone=phone)

        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
            logger.info("verified user %s", user)

        token, _ = Token.objects.get_or_create(user=user)

        user_serializer = UserSerializer(user)
        return Response(
            {
                "user": user_serializer.data,
                "token": token.key,
                "created": created,
            },
            status=status.HTTP_200_OK,
        )