from django.conf import settings
from django.db import models
from django.db.models import Q


class Category(models.Model):
    """Product category. A category can have a parent (one level of nesting)."""

    name = models.CharField("نام", max_length=100, unique=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="دسته والد",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent} › {self.name}"
        return self.name


class Product(models.Model):
    """An item listed by a seller, sold directly or by auction."""

    class SaleType(models.TextChoices):
        DIRECT = "direct", "فروش مستقیم"
        AUCTION = "auction", "مزایده"

    class Status(models.TextChoices):
        ACTIVE = "active", "فعال"
        SOLD = "sold", "فروخته‌شده"
        INACTIVE = "inactive", "غیرفعال"

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="فروشنده",
        on_delete=models.CASCADE,
        related_name="products",
        limit_choices_to={"role": "seller"},
    )
    category = models.ForeignKey(
        Category,
        verbose_name="دسته‌بندی",
        on_delete=models.PROTECT,
        related_name="products",
    )
    title = models.CharField("عنوان", max_length=200)
    description = models.TextField("توضیحات")
    price = models.DecimalField("قیمت (تومان)", max_digits=14, decimal_places=0)
    sale_type = models.CharField(
        "نوع فروش",
        max_length=10,
        choices=SaleType.choices,
        default=SaleType.DIRECT,
    )
    stock = models.PositiveIntegerField("موجودی", default=1)
    status = models.CharField(
        "وضعیت",
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        verbose_name = "کالا"
        verbose_name_plural = "کالاها"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gt=0),
                name="product_price_positive",
            ),
            models.CheckConstraint(
                condition=Q(sale_type="direct") | Q(stock__lte=1),
                name="auction_product_single_stock",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def is_auction(self):
        return self.sale_type == self.SaleType.AUCTION


class ProductImage(models.Model):
    """A picture of a product. Each product has at most one main image."""

    product = models.ForeignKey(
        Product,
        verbose_name="کالا",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField("تصویر", upload_to="products/%Y/%m/")
    is_main = models.BooleanField("تصویر اصلی", default=False)

    class Meta:
        verbose_name = "تصویر کالا"
        verbose_name_plural = "تصاویر کالا"
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_main=True),
                name="one_main_image_per_product",
            ),
        ]

    def __str__(self):
        return f"تصویر {self.product}"
# Create your models here.
