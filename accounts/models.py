from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


iranian_phone_validator = RegexValidator(regex=r"^\+989\d{9}$",
                                         message="Enter a valid Iranian mobile number (e.g., 09123456789).",
                                         code='invalid_iranian_mobile', )


class UserManager(BaseUserManager):
    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError('Users must have a phone number')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)

class User(AbstractBaseUser):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone'
    phone = models.CharField(max_length=15,validators=[iranian_phone_validator], unique=True)
    password = models.CharField(_("password"), max_length=128)

    objects = UserManager()

    def __str__(self):
        return str(self.phone)