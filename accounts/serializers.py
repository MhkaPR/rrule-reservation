from rest_framework import serializers

from accounts.models import User


class SendOtpSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(regex=r"^\+989\d{9}$")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone',)