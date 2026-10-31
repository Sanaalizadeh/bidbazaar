from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

iran_mobile_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message="شماره موبایل باید ۱۱ رقم باشد و با 09 شروع شود.",
)


class User(AbstractUser):
    """Custom user with a role (seller or buyer) and a mobile number."""

    class Role(models.TextChoices):
        SELLER = "seller", "فروشنده"
        BUYER = "buyer", "خریدار"

    email = models.EmailField("ایمیل", unique=True)
    phone_number = models.CharField(
        "شماره موبایل",
        max_length=11,
        unique=True,
        null=True,
        blank=True,
        validators=[iran_mobile_validator],
    )
    role = models.CharField(
        "نقش",
        max_length=10,
        choices=Role.choices,
        default=Role.BUYER,
    )

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_seller(self):
        return self.role == self.Role.SELLER

    @property
    def is_buyer(self):
        return self.role == self.Role.BUYER