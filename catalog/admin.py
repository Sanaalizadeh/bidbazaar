from django.contrib import admin

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "category", "sale_type", "price", "stock", "status", "created_at")
    list_filter = ("sale_type", "status", "category")
    search_fields = ("title", "description")
    inlines = [ProductImageInline]
# Register your models here.
