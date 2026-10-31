from django.conf import settings
from django.db import models
from django.db.models import Q


class Order(models.Model):
    """A purchase by a buyer: direct purchase or winning an auction."""

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار پرداخت"
        PAID = "paid", "پرداخت‌شده"
        SHIPPED = "shipped", "ارسال‌شده"
        DELIVERED = "delivered", "تحویل‌شده"
        CANCELLED = "cancelled", "لغوشده"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="خریدار",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    auction = models.OneToOneField(
        "auctions.Auction",
        verbose_name="مزایده مرتبط",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order",
    )
    status = models.CharField(
        "وضعیت",
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_price = models.DecimalField("مبلغ کل (تومان)", max_digits=14, decimal_places=0, default=0)
    shipping_address = models.TextField("آدرس ارسال")
    receiver_phone = models.CharField("تلفن گیرنده", max_length=11)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین تغییر", auto_now=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(total_price__gte=0),
                name="order_total_non_negative",
            ),
        ]

    def __str__(self):
        return f"سفارش #{self.pk} — {self.buyer}"


class OrderItem(models.Model):
    """One line of an order: a product, its quantity and its price at purchase time."""

    order = models.ForeignKey(
        Order,
        verbose_name="سفارش",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        verbose_name="کالا",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField("تعداد", default=1)
    unit_price = models.DecimalField("قیمت واحد (تومان)", max_digits=14, decimal_places=0)

    class Meta:
        verbose_name = "قلم سفارش"
        verbose_name_plural = "اقلام سفارش"
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_product_per_order",
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=1),
                name="order_item_quantity_min_1",
            ),
        ]

    def __str__(self):
        return f"{self.quantity} × {self.product}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
# Create your models here.
