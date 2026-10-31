from django.conf import settings
from django.db import models
from django.db.models import F, Q


class Auction(models.Model):
    """Auction settings and current state for a product sold by auction."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "زمان‌بندی‌شده"
        ACTIVE = "active", "در حال برگزاری"
        ENDED = "ended", "پایان‌یافته"
        CANCELLED = "cancelled", "لغوشده"

    product = models.OneToOneField(
        "catalog.Product",
        verbose_name="کالا",
        on_delete=models.CASCADE,
        related_name="auction",
        limit_choices_to={"sale_type": "auction"},
    )
    start_time = models.DateTimeField("زمان شروع")
    end_time = models.DateTimeField("زمان پایان")
    min_increment = models.DecimalField(
        "حداقل افزایش پیشنهاد (تومان)",
        max_digits=14,
        decimal_places=0,
        default=10000,
    )
    current_price = models.DecimalField(
        "بالاترین قیمت فعلی (تومان)",
        max_digits=14,
        decimal_places=0,
        blank=True,
    )
    status = models.CharField(
        "وضعیت",
        max_length=10,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    winning_bid = models.OneToOneField(
        "Bid",
        verbose_name="پیشنهاد برنده",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_auction",
    )
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        verbose_name = "مزایده"
        verbose_name_plural = "مزایده‌ها"
        ordering = ["end_time"]
        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F("start_time")),
                name="auction_end_after_start",
            ),
            models.CheckConstraint(
                condition=Q(min_increment__gt=0),
                name="auction_increment_positive",
            ),
        ]

    def __str__(self):
        return f"مزایده {self.product}"

    def save(self, *args, **kwargs):
        # The first price of an auction is the product's price.
        if self.current_price is None:
            self.current_price = self.product.price
        super().save(*args, **kwargs)


class Bid(models.Model):
    """A price offer by a buyer on an auction."""

    auction = models.ForeignKey(
        Auction,
        verbose_name="مزایده",
        on_delete=models.CASCADE,
        related_name="bids",
    )
    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="پیشنهاددهنده",
        on_delete=models.CASCADE,
        related_name="bids",
        limit_choices_to={"role": "buyer"},
    )
    amount = models.DecimalField("مبلغ پیشنهاد (تومان)", max_digits=14, decimal_places=0)
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "پیشنهاد قیمت"
        verbose_name_plural = "پیشنهادهای قیمت"
        ordering = ["-amount", "created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="bid_amount_positive",
            ),
        ]

    def __str__(self):
        return f"{self.bidder} — {self.amount:,} تومان"
# Create your models here.
